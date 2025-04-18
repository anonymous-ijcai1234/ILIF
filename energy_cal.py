import numpy as np
import torch.nn


# A. Operational cost  (Synapse Op)
def synaptic_op(input_size, output_size, kernel_size, neuron: str = None, T=None, fr_in=None, fr_out=None, stride=1):
    # MAC = 0.
    # ACC = 0.

    if isinstance(input_size, int):
        """ fully_connect"""
        if neuron == None:
            # ANN calculating
            MAC = input_size * output_size  # Weight
            ACC = output_size  # bias
        elif neuron == "LIF":
            # SNN LIF calculation
            spike_num_in = input_size * fr_in
            spike_num_out = output_size * fr_out

            MAC = T * output_size  # membrane potential leaky

            ACC_w = spike_num_in * input_size * output_size  # synapse weight
            ACC_b = T * spike_num_out

            ACC = ACC_w + ACC_b
        elif neuron == "ILIF":
            # SNN ILIF calculation
            spike_num_in = input_size * fr_in
            spike_num_out = output_size * fr_out

            MAC = T * output_size * 2  # membrane potential leaky

            ACC_w = spike_num_in * input_size * output_size  # synapse weight
            ACC_b = T * spike_num_out * 3

            ACC = ACC_w + ACC_b
        else:
            raise NotImplementedError

    else:
        """convolution"""
        C_in, H_in, W_in = input_size
        C_out, H_out, W_out = output_size
        _, _, H_kernel, W_kernel = kernel_size
        # stride = kerner.stride

        if neuron == None:
            # ANN calculating
            MAC = C_out * H_out * W_out * C_in * H_kernel * W_kernel  # Weight
            ACC = C_out * H_out * W_out  # bias
        elif neuron == "LIF":
            # SNN LIF calculation
            spike_num_in = (C_in * H_in * W_in) * fr_in
            spike_num_out = (C_out * H_out * W_out) * fr_out

            MAC = T * C_out * H_out * W_out  # membrane potential leaky

            ACC_w = spike_num_in * (H_kernel // stride) * (W_kernel // stride) * C_out  # Weight op
            ACC_b = T * C_out * H_out * W_out + spike_num_out  # Bias op

            ACC = ACC_w + ACC_b

        elif neuron == "ILIF":
            # SNN LIF calculation
            spike_num_in = (C_in * H_in * W_in) * fr_in
            spike_num_out = (C_out * H_out * W_out) * fr_out

            MAC = T * C_out * H_out * W_out * 2  # membrane potential leaky
            ACC_w = spike_num_in * (H_kernel // stride) * (W_kernel // stride) * C_out  # Weight op
            ACC_b = T * C_out * H_out * W_out + spike_num_out * 3  # Bias op

            ACC = ACC_w + ACC_b
        else:
            raise NotImplementedError

    return MAC, ACC


# B. Memory cost
def memory_cost(input_size, output_size, kernel_size=None, neuron: str = None, T=None, fr_in=None, fr_out=None,
                stride=1):
    # read_in = 0.
    # read_params = 0.
    # read_potential = 0.
    # write_out = 0.
    # write_potential = 0.

    if isinstance(input_size, int):
        """ fully_connect"""

        if neuron == None:
            read_in = input_size
            read_params = (input_size + 1) * output_size
            read_potential = 0.
            write_out = output_size
            write_potential = 0.
        elif neuron == "LIF":
            spike_num_in = input_size * fr_in
            spike_num_out = output_size * fr_out

            read_in = spike_num_in
            read_params = spike_num_in * output_size + output_size
            read_potential = (spike_num_in + 1) * spike_num_out
            write_out = spike_num_out
            write_potential = spike_num_in * output_size + output_size
        elif neuron == "ILIF":
            spike_num_in = input_size * fr_in
            spike_num_out = output_size * fr_out

            read_in = spike_num_in
            read_params = spike_num_in * output_size + output_size
            read_potential = (spike_num_in + 1) * spike_num_out * 4
            write_out = spike_num_out
            write_potential = (spike_num_in * output_size + output_size) * 2
        else:
            raise NotImplementedError


    else:
        """convolution"""
        C_in, H_in, W_in = input_size
        C_out, H_out, W_out = output_size
        _, _, H_kernel, W_kernel = kernel_size

        if neuron == None:
            read_in = C_out * C_in * H_out * W_out * H_kernel * W_kernel
            read_params = (C_in * W_kernel * H_kernel + 1) * C_out * W_out * H_out
            read_potential = 0.
            write_out = C_out * W_out * H_out
            write_potential = 0.
        elif neuron == "LIF":
            spike_num_in = (C_in * H_in * W_in) * fr_in
            spike_num_out = (C_out * H_out * W_out) * fr_out

            read_in = spike_num_in
            read_params = spike_num_in * C_out * W_kernel * H_kernel + C_out * W_out * H_out
            read_potential = spike_num_in * C_out * W_kernel * H_kernel + C_out * W_out * H_out
            write_out = spike_num_out
            write_potential = spike_num_in * C_out * W_kernel * H_kernel + C_out * W_out * H_out
        elif neuron == "ILIF":
            spike_num_in = (C_in * H_in * W_in) * fr_in
            spike_num_out = (C_out * H_out * W_out) * fr_out

            read_in = spike_num_in
            read_params = spike_num_in * C_out * W_kernel * H_kernel + C_out * W_out * H_out
            read_potential = (spike_num_in * C_out * W_kernel * H_kernel + C_out * W_out * H_out) * 4
            write_out = spike_num_out
            write_potential = (spike_num_in * C_out * W_kernel * H_kernel + C_out * W_out * H_out) * 2
        else:
            raise NotImplementedError

    return read_in, read_params, read_potential, write_out, write_potential  # a, b, c, d, e


# C. Addressing
def addressing_cost(input_size, output_size, kernel_size=None, neuron: str = None, T=None, fr_in=None, fr_out=None,
                    stride=1):
    # MAC = 0.
    # ACC = 0.

    if isinstance(input_size, int or float):
        """ fully_connect"""
        if neuron == None:
            # ANN calculating
            MAC = 0.  # Weight
            ACC = input_size + output_size  # bias

        elif neuron == "LIF":
            # SNN LIF calculation
            spike_num_in = input_size * fr_in
            spike_num_out = output_size * fr_out

            MAC = 0.
            ACC = spike_num_in * output_size

        elif neuron == "ILIF":
            # SNN LIF calculation
            spike_num_in = input_size * fr_in
            spike_num_out = output_size * fr_out

            MAC = 0.
            ACC = spike_num_in * output_size * 3
        else:
            raise NotImplementedError

    else:
        """convolution"""
        C_in, H_in, W_in = input_size
        C_out, H_out, W_out = output_size
        _, _, H_kernel, W_kernel = kernel_size
        # stride = kerner.stride

        if neuron == None:
            # ANN calculating
            MAC = 0.
            ACC = C_in * H_in * W_in \
                  + C_out * H_out * W_out \
                  + C_out * H_kernel * W_kernel
        elif neuron == "LIF":
            # SNN LIF calculation
            spike_num_in = (C_in * H_in * W_in) * fr_in
            spike_num_out = (C_out * H_out * W_out) * fr_out

            MAC = spike_num_in * 2
            ACC = spike_num_in * C_out * H_kernel * W_kernel
        elif neuron == "ILIF":
            # SNN LIF calculation
            spike_num_in = (C_in * H_in * W_in) * fr_in
            spike_num_out = (C_out * H_out * W_out) * fr_out

            MAC = spike_num_in * 2 * 2
            ACC = spike_num_in * C_out * H_kernel * W_kernel * 2

        else:
            raise NotImplementedError

    return MAC, ACC


# in paper  E_RdRAM = E_WrRAM
# For SRAM memory accesses, we compute a linear interpolation function based on 3 particular values :
# 8 kB (10pJ), 32 kB (20pJ) and 1 MB (100pJ).
# This function enables to compute the energy cost of a memory access knowing the memory size
# (i.e. knowing the network hyperparameters).
def E_func(Memory):
    E1 = 10  # pj
    E2 = 20  # pj
    E3 = 100  # pj

    m1 = 8 * 1024
    m2 = 32 * 1024
    m3 = 1024 * 1024
    if Memory <= m1:
        # E = Memory
        E = ((E1 - 0) / (m1 - 0)) * (Memory - 0)
    elif (Memory > m1) and (Memory <= m2):
        E = ((E2 - E1) / (m2 - m1)) * (Memory - m1)
    elif (Memory > m2) and (Memory <= m3):
        E = ((E3 - E2) / (m3 - m2)) * (Memory - m2)
    else:
        E = E3
        # raise NotImplementedError
    return E


# E_RdRAM = E_func()
# E_WrRAM = E_func()
#
# def calculation_E(read_in, read_params, read_potential, write_out, write_potential, MAC_op, ACC_op, MAC_adr, ACC_adr):
#     return read_in * E_func(read_in)

def calculate_all_operations(net_layers, neuron, T, spike_fr):
    mac_op = 0.
    acc_op = 0.

    read_in, read_params, read_potential, write_out, write_potential = 0., 0., 0., 0., 0.

    mac_addr = 0.
    acc_addr = 0.

    for i in range(len(net_layers)):

        input_size, output_size, kernel_size, stride = net_layers[i]

        if i == 0:
            MAC_op, ACC_op = synaptic_op(input_size=input_size, output_size=output_size, kernel_size=kernel_size,
                                         neuron=neuron, T=T, fr_in=1., fr_out=spike_fr[0], stride=stride)
            a, b, c, d, e = memory_cost(input_size=input_size, output_size=output_size, kernel_size=kernel_size,
                                        neuron=neuron, T=T, fr_in=1., fr_out=spike_fr[0], stride=stride)
            ma, aa = addressing_cost(input_size=input_size, output_size=output_size,
                                     kernel_size=kernel_size,
                                     neuron=neuron, T=T, fr_in=1., fr_out=spike_fr[0], stride=stride)
        else:
            fr_in = spike_fr[i - 1]

            if i == len(net_layers) - 1:
                fr_out = 0.
            else:
                fr_out = spike_fr[i]
            MAC_op, ACC_op = synaptic_op(input_size=input_size, output_size=output_size, kernel_size=kernel_size,
                                         neuron=neuron, T=T, fr_in=fr_in, fr_out=fr_out, stride=stride)
            a, b, c, d, e = memory_cost(input_size=input_size, output_size=output_size, kernel_size=kernel_size,
                                        neuron=neuron, T=T, fr_in=fr_in, fr_out=fr_out, stride=stride)
            ma, aa = addressing_cost(input_size=input_size, output_size=output_size,
                                     kernel_size=kernel_size,
                                     neuron=neuron, T=T, fr_in=fr_in, fr_out=fr_out, stride=stride)

        mac_op += MAC_op
        acc_op += ACC_op

        read_in += a
        read_params += b
        read_potential += c
        write_out += d
        write_potential += e

        mac_addr += ma
        acc_addr += aa
    return mac_op, acc_op, read_in, read_params, read_potential, write_out, write_potential, mac_addr, acc_addr

def compute_sop_ac_mac(net_layers, neuron, T, spike_fr):
    ACs = 0.0
    MACs = 0.0

    for i, (input_size, output_size, kernel_size, stride) in enumerate(net_layers):
        if i == len(net_layers) - 1:
            continue  # 最后一层无 fanout

        fr = spike_fr[i] if neuron is not None else None

        if isinstance(input_size, int):
            # fully connected
            N_in = input_size
            N_out = output_size
            fanout = N_out

            if neuron is None:
                MACs += N_in * N_out
            else:
                spike_num = N_in * fr
                ACs += T * spike_num * fanout

                # ✅ 加上 SNN 自身的 MAC（membrane更新）
                if neuron == "LIF":
                    MACs += T * N_out
                elif neuron == "ILIF":
                    MACs += T * N_out * 3

        else:
            # convolution
            C_in, H_in, W_in = input_size
            C_out, H_out, W_out = output_size
            _, _, K_h, K_w = kernel_size
            N_in = C_in * H_in * W_in
            fanout = C_out * (K_h * K_w)
            N_out = C_out * H_out * W_out

            if neuron is None:
                MACs += C_out * H_out * W_out * C_in * K_h * K_w
            else:
                spike_num = N_in * fr
                ACs += T * spike_num * fanout

                # ✅ 加上 SNN 自身的 MAC（membrane更新）
                if neuron == "LIF":
                    MACs += T * N_out
                elif neuron == "ILIF":
                    MACs += T * N_out * 2

    return ACs, MACs

# input_size, output_size, kernel_size=None, stride
resnet_18_cifar10_network = [
    [(3, 32, 32), (64, 32, 32), (3, 64, 3, 3), 1],
    [(64, 32, 32), (64, 32, 32), (64, 64, 3, 3), 1],

    [(64, 32, 32), (64, 32, 32), (64, 64, 3, 3), 1],
    [(64, 32, 32), (64, 32, 32), (64, 64, 3, 3), 1],

    [(64, 32, 32), (64, 32, 32), (64, 64, 3, 3), 1],
    [(64, 32, 32), (128, 16, 16), (64, 128, 3, 3), 2],

    [(128, 16, 16), (128, 16, 16), (128, 128, 3, 3), 1],
    [(128, 16, 16), (128, 16, 16), (128, 128, 3, 3), 1],

    [(128, 16, 16), (128, 16, 16), (128, 128, 3, 3), 1],
    [(128, 16, 16), (256, 8, 8), (128, 256, 3, 3), 2],

    [(256, 8, 8), (256, 8, 8), (256, 256, 3, 3), 1],
    [(256, 8, 8), (256, 8, 8), (256, 256, 3, 3), 1],

    [(256, 8, 8), (256, 8, 8), (256, 256, 3, 3), 1],
    [(256, 8, 8), (512, 4, 4), (256, 512, 3, 3), 2],

    [(512, 4, 4), (512, 4, 4), (512, 512, 3, 3), 1],
    [(512, 4, 4), (512, 4, 4), (512, 512, 3, 3), 1],

    [(512, 4, 4), (512, 4, 4), (512, 512, 3, 3), 1],
    [512, 10, None, None],  # ignoring pooling
]

# input_size, output_size, kernel_size=None, stride
resnet_18_cifar100_network = [
    [(3, 32, 32), (64, 32, 32), (3, 64, 3, 3), 1],
    [(64, 32, 32), (64, 32, 32), (64, 64, 3, 3), 1],

    [(64, 32, 32), (64, 32, 32), (64, 64, 3, 3), 1],
    [(64, 32, 32), (64, 32, 32), (64, 64, 3, 3), 1],

    [(64, 32, 32), (64, 32, 32), (64, 64, 3, 3), 1],
    [(64, 32, 32), (128, 16, 16), (64, 128, 3, 3), 2],

    [(128, 16, 16), (128, 16, 16), (128, 128, 3, 3), 1],
    [(128, 16, 16), (128, 16, 16), (128, 128, 3, 3), 1],

    [(128, 16, 16), (128, 16, 16), (128, 128, 3, 3), 1],
    [(128, 16, 16), (256, 8, 8), (128, 256, 3, 3), 2],

    [(256, 8, 8), (256, 8, 8), (256, 256, 3, 3), 1],
    [(256, 8, 8), (256, 8, 8), (256, 256, 3, 3), 1],

    [(256, 8, 8), (256, 8, 8), (256, 256, 3, 3), 1],
    [(256, 8, 8), (512, 4, 4), (256, 512, 3, 3), 2],

    [(512, 4, 4), (512, 4, 4), (512, 512, 3, 3), 1],
    [(512, 4, 4), (512, 4, 4), (512, 512, 3, 3), 1],

    [(512, 4, 4), (512, 4, 4), (512, 512, 3, 3), 1],
    [512, 100, None, None],  # ignoring pooling
]

# input_size, output_size, kernel_size=None, stride
vgg11_dvsgesture_network = [
    [(2, 128, 128), (64, 128, 128), (2, 64, 3, 3), 1],
    # pooling
    [(64, 64, 64), (128, 64, 64), (64, 128, 3, 3), 1],
    # pooling
    [(128, 32, 32), (256, 32, 32), (128, 256, 3, 3), 1],
    [(256, 32, 32), (256, 32, 32), (256, 256, 3, 3), 1],
    # pooling
    [(256, 16, 16), (512, 16, 16), (256, 512, 3, 3), 1],
    [(512, 16, 16), (512, 16, 16), (512, 512, 3, 3), 1],
    # pooling
    [(512, 8, 8), (512, 8, 8), (512, 512, 3, 3), 1],
    [(512, 8, 8), (512, 8, 8), (512, 512, 3, 3), 1],
    #  adaptive pooling
    [25088, 11, None, None]
]

# input_size, output_size, kernel_size=None, stride
vgg11_dvscifar_network = [
    [(2, 48, 48), (64, 48, 48), (2, 64, 3, 3), 1],
    # pooling
    [(64, 24, 24), (128, 24, 24), (64, 128, 3, 3), 1],
    # pooling
    [(128, 12, 12), (256, 12, 12), (128, 256, 3, 3), 1],
    [(256, 12, 12), (256, 12, 12), (256, 256, 3, 3), 1],
    # pooling
    [(256, 6, 6), (512, 6, 6), (256, 512, 3, 3), 1],
    [(512, 6, 6), (512, 6, 6), (512, 512, 3, 3), 1],
    # pooling
    [(512, 3, 3), (512, 3, 3), (512, 512, 3, 3), 1],
    [(512, 3, 3), (512, 3, 3), (512, 512, 3, 3), 1],
    # adaptive pooling
    [25088, 10, None, None]
]

data = {
    'cifar10': {
        'ILIF': np.array(
            [26.220, 18.600, 16.571, 13.739, 19.376, 15.540, 15.299, 8.492, 13.584, 12.831, 10.616, 7.050, 7.259, 6.929, 5.068, 4.902, 3.127]) / 100,
        'LIF': np.array(
            [28.665, 20.232, 19.962, 16.252, 22.376, 18.391, 17.267, 8.834, 15.010, 13.748, 12.336, 8.140, 9.659, 9.108, 5.598, 6.649, 4.742]) / 100
    },
    'cifar100': {
        'ILIF': np.array(
            [19.727, 10.242, 10.399, 10.920, 15.569, 13.471, 11.949, 6.813, 15.342, 10.395, 7.733, 6.829, 7.834, 4.770, 3.116, 4.474, 11.213]) / 100,
        'LIF': np.array(
            [18.134, 9.223, 10.650, 11.705, 15.850, 13.851, 13.164, 5.945, 17.006, 10.682, 8.649, 5.603, 9.487, 5.644, 3.814, 5.010, 16.382]) / 100
    },
    'dvsgesture': {
        'ILIF': np.array([4.351, 2.274, 1.428, 1.733, 1.067, 0.878, 0.895,0.231]) / 100,
        'LIF': np.array([5.096, 2.372, 1.724, 2.134, 1.682, 1.147, 1.400, 0.438]) / 100
    },
    'dvscifar': {
        'ILIF': np.array([8.411, 6.763, 8.155, 5.413, 4.748, 2.136, 2.311, 1.237]) / 100,
        'LIF': np.array([7.820, 8.173, 9.246, 7.140, 5.676, 3.561, 2.816, 2.146]) / 100
    }
}

network = {
    "cifar10": resnet_18_cifar10_network,
    "cifar100": resnet_18_cifar100_network,
    "dvscifar": vgg11_dvscifar_network,
    "dvsgesture": vgg11_dvsgesture_network,
}

Timestep = {
    "cifar10": 6,
    "cifar100": 6,
    "dvscifar": 10,
    "dvsgesture": 20,
}

if __name__ == '__main__':
    # ref: Lemaire, E., et al.An analytical estimation of spiking neural networks energy efficiency. In International Conference on Neural Information Processing, 2022.

    # task = "cifar10"
    # task = "cifar100"
    task = "dvscifar"
    # task = "dvsgesture"
    # neuron = "LIF"
    neuron = "ILIF"
    # neuron = None  # ANN

    T = Timestep[task]
    net_layers = network[task]
    spike_fr = data[task][neuron] if neuron is not None else [None] * 18

    mac_op, acc_op, read_in, read_params, read_potential, write_out, write_potential, mac_addr, acc_addr = calculate_all_operations(
        net_layers, neuron, T, spike_fr)

    ACs, MACs = compute_sop_ac_mac(net_layers, neuron, T, spike_fr)
    print(f"ACs = {ACs / 1e6:.2f} M, MACs = {MACs / 1e6:.2f} M")

    SOP_energy = ACs * 0.9 + MACs * 4.6  # unit: pJ
    print(f"SOP Energy = {SOP_energy / 1e6:.3f} µJ")
