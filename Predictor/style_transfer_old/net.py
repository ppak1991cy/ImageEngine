import torch.nn as nn
from torch.nn import init
from Predictor.style_transfer_old.layer import *
import numpy as np


class Generator(torch.nn.Module):
    def __init__(self, nb_style=None):
        super(Generator, self).__init__()
        self.nb_style = nb_style
        self.psr = PixelShuffleReverse(4)

        self.conv1 = ConvLayer(48, 128, 3, 1)
        self.conv2 = NormConvBlock(128, 128, 3, 1, nb_style)
        self.conv3 = NormConvBlock(128, 128, 3, 1, nb_style)
        self.conv4 = NormConvBlock(128, 128, 3, 1, nb_style)
        self.conv5 = NormConvBlock(128, 128, 3, 1, nb_style)

        self.conv6 = NormConvBlock(128, 128, 3, 1, nb_style)
        self.conv7 = NormConvBlock(128, 128, 3, 1, nb_style)
        self.conv8 = NormConvBlock(128, 128, 3, 1, nb_style)
        self.conv9 = NormConvBlock(128, 128, 3, 1, nb_style)
        self.conv10 = NormConvBlock(128, 128, 3, 1, nb_style)

        self.ps = nn.PixelShuffle(4)
        self.conv11 = NormConvBlock(8, 3, 3, 1, nb_style)

    def forward(self, x, style_coefficient=None, ins_norm=False):
        uni_noise = init.normal_(x.clone(), 0, 0.03)
        x_noise = x + uni_noise
        x_psr = self.psr(x_noise)
        neck = self.conv2(self.conv1(x_psr), style_coefficient, ins_norm)

        neck = self.conv3(neck, style_coefficient, ins_norm)
        neck = self.conv4(neck, style_coefficient, ins_norm)
        neck = self.conv5(neck, style_coefficient, ins_norm)
        neck = self.conv6(neck, style_coefficient, ins_norm)
        neck = self.conv7(neck, style_coefficient, ins_norm)
        neck = self.conv8(neck, style_coefficient, ins_norm)
        neck = self.conv9(neck, style_coefficient, ins_norm)
        neck = self.conv10(neck, style_coefficient, ins_norm)

        y_ps = self.conv11(self.ps(neck), style_coefficient, ins_norm)
        return y_ps


class ConvLayer(torch.nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, stride):
        super(ConvLayer, self).__init__()
        reflection_padding = int(np.floor(kernel_size / 2))
        if reflection_padding == 0:
            self.reflection_pad = None
        else:
            self.reflection_pad = nn.ReflectionPad2d(reflection_padding)
        self.conv2d = nn.Conv2d(in_channels, out_channels, kernel_size, stride, bias=False)

    def forward(self, x):
        if self.reflection_pad is not None:
            x = self.reflection_pad(x)
        out = self.conv2d(x)
        return out


class NormConvBlock(torch.nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, stride, nb_style):
        super(NormConvBlock, self).__init__()
        self.ins_norm = InstanceNorm2d(in_channels)
        self.cond_ins_norm = ConditionalInstanceNorm2d(nb_style, in_channels)
        self.act_fn = nn.PReLU(in_channels)
        self.conv2d = ConvLayer(in_channels, out_channels, kernel_size, stride)

    def forward(self, x, style_coefficient=None, ins_norm=False):
        if ins_norm:
            norm_x = self.ins_norm(x)
        else:
            norm_x = self.cond_ins_norm(x, style_coefficient)
        out = self.act_fn(norm_x)
        out = self.conv2d(out)
        return out
