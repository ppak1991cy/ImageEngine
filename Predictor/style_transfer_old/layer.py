import torch

from torch.nn import Module
from torch.nn.parameter import Parameter
import torch.nn.functional as F


class PixelShuffleReverse(Module):
    def __init__(self, upscale_factor):
        super(PixelShuffleReverse, self).__init__()
        self.upscale_factor = upscale_factor

    def forward(self, input):
        batch_size, channels, h, w = input.size()
        out_channels = channels*self.upscale_factor*self.upscale_factor
        out_h = int(h/self.upscale_factor)
        out_w = int(w/self.upscale_factor)
        if h % self.upscale_factor != 0 or w % self.upscale_factor != 0:
            raise ValueError('got input height {} width {}, but both should be divisible by upscale_factor {}'
                             .format(h, w, self.upscale_factor))
        input_view = input.contiguous().view(batch_size, channels, out_h, self.upscale_factor,
                                             out_w, self.upscale_factor)
        shuffle_out = input_view.permute(0, 1, 3, 5, 2, 4).contiguous()
        return shuffle_out.view(batch_size, out_channels, out_h, out_w)


class InstanceNorm2d(Module):
    def __init__(self, num_features):
        """ only support batch_size 1 in training phase, but no this limit in testing phase"""
        super(InstanceNorm2d, self).__init__()
        self.num_features = num_features
        self.weight = Parameter(torch.ones(num_features))
        self.bias = Parameter(torch.zeros(num_features))
        self.register_buffer('running_mean', torch.zeros(num_features))
        self.register_buffer('running_var', torch.ones(num_features))
        self.reset_parameters()

    def reset_parameters(self):
        self.running_mean.zero_()
        self.running_var.fill_(1)
        self.weight.data.fill_(1)
        self.bias.data.zero_()

    def forward(self, input):
        B, C, H, W = input.size()
        input_view = input.view(1, B*C, H, W)
        output_view = F.batch_norm(input_view, self.running_mean.repeat(B), self.running_var.repeat(B),
                                   self.weight.repeat(B), self.bias.repeat(B), training=True, momentum=0., eps=1e-5)
        output = output_view.view(B, C, H, W)
        return output


class ConditionalInstanceNorm2d(Module):
    def __init__(self, nb_style, num_features):
        """ only support batch_size 1 in training phase, but no this limit in testing phase"""
        super(ConditionalInstanceNorm2d, self).__init__()
        self.num_features = num_features
        self.nb_style = nb_style
        self.weight = Parameter(torch.ones(nb_style, num_features))
        self.bias = Parameter(torch.zeros(nb_style, num_features))
        self.register_buffer('running_mean', torch.zeros(num_features))
        self.register_buffer('running_var', torch.ones(num_features))
        self.reset_parameters()

    def reset_parameters(self):
        self.running_mean.zero_()
        self.running_var.fill_(1)
        self.weight.data.fill_(1)
        self.bias.data.zero_()

    def forward(self, input, style_coefficient):
        """ style_coefficient: shape (batch_size, nb_style), in training phase all training sample have the same
        style_coefficient, which means we learn one style in a single batch. While in inference phase, each training sample
        could have different style to learn. Moreover, each sample's coefficient could be a prob distribution,
        indicate the way you want to mixing with each style.
        """
        B, C, H, W = input.size()
        weight_expand = self.weight.unsqueeze(0).expand(B, self.nb_style, self.num_features)
        bias_expand = self.bias.unsqueeze(0).expand(B, self.nb_style, self.num_features)
        style_coefficient_expand = style_coefficient.unsqueeze(2).expand(B, self.nb_style, self.num_features)
        conditional_weight = torch.sum(weight_expand*style_coefficient_expand, dim=1).squeeze(1)
        conditional_bias = torch.sum(bias_expand*style_coefficient_expand, dim=1).squeeze(1)
        if self.training:
            if input.size(0) != 1:
                raise ValueError('got {}-batch size, expected {}'
                                 .format(input.size(0), 1))
            return F.batch_norm(input, self.running_mean, self.running_var, conditional_weight.squeeze(0),
                                conditional_bias.squeeze(0), training=True, momentum=0., eps=1e-5)

        input_view = input.view(1, B*C, H, W)
        output_view = F.batch_norm(input_view, self.running_mean.repeat(B), self.running_var.repeat(B),
                                   conditional_weight, conditional_bias, training=True, momentum=0., eps=1e-5)
        output = output_view.view(B, C, H, W)
        return output
