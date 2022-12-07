from .models.unet import UNet, FDMUNet, ConcatGeoUNet, GeoUNet, EncoderConv
from .models.deeplab import DeeplabV3p
from .models.resnetunet import UNetResNet

import torch
import torch.nn as nn

class MultiTaskNet(nn.Module):

    def __init__(self, base_model, use_time, pooling, after_encoder):

        super(MultiTaskNet, self).__init__()

        self.use_time = use_time
        self.pooling = pooling

        if self.use_time:
            self.name = "GeoTimeMultiTaskNet"

            self.time_predictor = nn.Sequential(
                nn.Linear(in_features=64*64*64, out_features=512),
                nn.BatchNorm1d(512),
                nn.ReLU(inplace=True),
                nn.Linear(in_features=512, out_features=128),
                nn.BatchNorm1d(128),
                nn.ReLU(inplace=True),
                nn.Linear(in_features=128, out_features=4),
                )
        else:
            self.name = "GeoMultiTaskNet"

        self.base_model = base_model
        self.after_encoder = after_encoder

        if self.after_encoder:
            if not self.pooling:
                if self.base_model.name == "ResUNet":
                    input_dim = 32768
                else:
                    input_dim = 65536
            else: 
                self.max_pool = nn.MaxPool2d(8)
                if self.base_model.name == "ResUNet":
                    input_dim = 512
                else:
                    input_dim = 1024
        else:
            if not self.pooling:
                if self.base_model.name == "ResUNet":
                    input_dim = 32
                else:
                    input_dim = 16
                self.ch1 = EncoderConv(input_dim, 32)                
                self.ch2 = EncoderConv(32, 64)
                input_dim = 64*64*64
            else: 
                self.max_pool = nn.MaxPool2d(8)
                if self.base_model.name == "ResUNet":
                    input_dim = 32*32*32
                else:
                    input_dim = 16*32*32           
            
        self.coords_predictor = nn.Sequential(
            nn.Linear(in_features=input_dim, out_features=1024),
            nn.BatchNorm1d(1024),
            nn.ReLU(inplace=True),
            nn.Linear(in_features=1024, out_features=256),
            nn.BatchNorm1d(256),
            nn.ReLU(inplace=True),
            nn.Linear(in_features=256, out_features=256),
            )

    def forward(self, x):

        _, _, x5, x, x_2d = self.base_model(x)

        if self.pooling:
            if self.after_encoder:
                x = self.max_pool(x5)
            else:
                x = self.max_pool(x)
        else:
            if self.after_encoder:
                x = x5
            else:
                x = self.ch1(x) #b, 32, 128, 128
                x = self.ch2(x) #b, 64, 64, 64

        x_coord = self.coords_predictor(x.view(x.size(0), -1))

        if self.use_time:
            x_time = self.time_predictor(x.view(x.size(0), -1))
            return x_2d, x_coord, x_time
        else:
            return x_2d, x_coord         


################LOADING RIGHT MODEL
def choose_model(model_params, geo_data):
    if model_params["model_name"] == "unet":
        model =  UNet(n_channels = model_params['num_channels'], 
                n_classes = model_params['num_classes'], 
                drop_out = model_params['dropout'])
        if model_params["constraint_name"] == "multitask_strategy":
            model = MultiTaskNet(model, model_params["mt_time"], model_params["pooling"], model_params["after_encoder"])
    elif model_params["model_name"] == "keepitsimple":
        model = FDMUNet(n_channels = model_params['num_channels'], 
           n_classes = model_params['num_classes'], 
           drop_out = model_params['dropout'])
    elif model_params["model_name"] == "concat_geounet":
        model = ConcatGeoUNet(n_channels = model_params['num_channels'], 
           n_classes = model_params['num_classes'], 
           geoinfo= geo_data,
           drop_out = model_params['dropout'],
           use_time= model_params['use_time'],
           use_geo= model_params['use_geo'],
           use_domains= model_params['use_domains'],
           use_coords_pos_enc = model_params['use_coords_pos_enc'],
           use_label_distr = model_params['use_label_distr'])
    elif model_params["model_name"] == "geounet":
        model = GeoUNet(n_channels = model_params['num_channels'], 
           n_classes = model_params['num_classes'], 
           geoinfo= geo_data,
           drop_out = model_params['dropout'],
           use_time= model_params['use_time'],
           use_geo= model_params['use_geo'],
           use_domains= model_params['use_domains'],
           use_coords_pos_enc = model_params['use_coords_pos_enc'],
           use_label_distr = model_params['use_label_distr']
           )  
    elif model_params["model_name"] == "resunet18":
        model = UNetResNet(18, 
                n_classes = model_params['num_classes'], 
                n_channels = model_params['num_channels'], 
                num_filters=32, 
                dropout_2d=0.2,
                pretrained=True, 
                is_deconv=False)
        if model_params["constraint_name"] == "multitask_strategy":
            model = MultiTaskNet(model, model_params["mt_time"], model_params["pooling"], model_params["after_encoder"])
    else:
        raise Exception("This model is not implemented")       
    print(model.name)
    return model
