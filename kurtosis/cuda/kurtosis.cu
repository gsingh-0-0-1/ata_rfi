#include <cuda_runtime.h>
#include <stdio.h>
#include <random>
#include <iostream>

typedef struct comp_float {
    float real;
    float imag;
} comp_float_t;


/*
// CUDA kernel to compute the mean
__global__ void computeChannelMean(
    const float* block, float* output,
    int N_ANTS, int N_CHANS, int N_SAMPS, int N_POLS) {

    // Compute indices
    int ant = blockIdx.x;    // Antenna index
    int chan = blockIdx.y;   // Channel index
    int pol = threadIdx.x;   // Polarization index

    if (ant < N_ANTS && chan < N_CHANS && pol < N_POLS) {
        // Compute the mean for this channel
        float sum = 0.0f;
        for (int samp = 0; samp < N_SAMPS; ++samp) {
            int idx = ((ant * N_CHANS + chan) * N_SAMPS + samp) * N_POLS + pol;
            sum += block[idx];
        }
        float mean = sum / N_SAMPS;

        // Write the result to the output array
        int out_idx = ((ant * N_CHANS + chan) * 1 + 0) * N_POLS + pol;
        output[out_idx] = mean;
    }
}

// Host function to call the kernel
void calculateMean(
    const float* d_block, float* d_output,
    int N_ANTS, int N_CHANS, int N_SAMPS, int N_POLS) {

    dim3 gridDim(N_ANTS, N_CHANS);    // One block per antenna and channel
    dim3 blockDim(N_POLS);           // One thread per polarization

    computeChannelMean<<<gridDim, blockDim>>>(
        d_block, d_output, N_ANTS, N_CHANS, N_SAMPS, N_POLS);
}
*/

// CUDA kernel to compute sk_array
__global__ void computeSkArray(
    comp_float_t* block,
    int N_ANTS, int N_CHANS, int N_SAMPS, int N_POLS) {//, int m) {


    // Compute indices
    int ant = blockIdx.x;    // Antenna index
    int chan = blockIdx.y;   // Channel index
    int pol = threadIdx.x;   // Polarization index

    if (ant < N_ANTS && chan < N_CHANS && pol < N_POLS) {
        // Initialize sums
        float s1 = 0.0f;
        float s2 = 0.0f;

        // Compute s1 (sum of elements) and s2 (sum of squares)
        for (int samp = 0; samp < N_SAMPS; samp++) {
            int idx = ((ant * N_CHANS + chan) * N_SAMPS + samp) * N_POLS + pol;
            comp_float_t value = block[idx];

            float v2 = value.real * value.real + value.imag * value.imag;

            s1 += v2;
            s2 += v2 * v2;
        }

        // Compute sk value
        float sk = ((N_SAMPS + 1.0f) / (N_SAMPS - 1.0f)) * ((N_SAMPS * (s2 / (s1 * s1))) - 1.0f);

        // based on sk we can zap the channel
        // TODO: change sk thresholds / properly apply from sklim
        if (sk > 3) {
            int chan_start = ((ant * N_CHANS + chan) * N_SAMPS + 0) * N_POLS + pol;
            for (int j = chan_start; j < chan_start + N_SAMPS * N_POLS; j = j + N_POLS) {
                block[j].real = 0.0;
                block[j].imag = 0.0;
            }
        }

        // Write the result to the output array
        // int out_idx = ((ant * N_CHANS + chan) * 1 + 0) * N_POLS + pol;
        // output[out_idx] = sk;
    }
}

// Host function to call the kernel
void calculateSkArray(
    comp_float_t* d_block,
    int N_ANTS, int N_CHANS, int N_SAMPS, int N_POLS) {//, int m) {

    dim3 gridDim(N_ANTS, N_CHANS);    // One block per antenna and channel
    dim3 blockDim(N_POLS);           // One thread per polarization

    computeSkArray<<<gridDim, blockDim>>>(
        d_block, N_ANTS, N_CHANS, N_SAMPS, N_POLS);//, m);
}


int main() {
    // Define dimensions
    int N_ANTS = 4, N_CHANS = 4, N_SAMPS = 8, N_POLS = 2;

    // Allocate memory on host
    size_t input_size = N_ANTS * N_CHANS * N_SAMPS * N_POLS * sizeof(comp_float_t);
    // size_t output_size = N_ANTS * N_CHANS * 1 * N_POLS * sizeof(float);
    comp_float_t* h_block = (comp_float_t*)malloc(input_size);
    // float* h_output = (float*)malloc(output_size);

    std::random_device rd{};
    std::mt19937 gen{rd()};

    std::normal_distribution d{0.0, 1.0};

    auto randnorm = [&d, &gen]{ return d(gen); };

    // Initialize input data
    for (int i = 0; i < N_ANTS * N_CHANS * N_SAMPS * N_POLS; ++i) {
        h_block[i].imag = static_cast<float>(randnorm());
        h_block[i].real = static_cast<float>(randnorm());
    }

    // pollute the first two channels
    for (int i = 0; i < 4; i++) {
        h_block[i].real = 100.0f;
    }


    // print block before
    for (int ant = 0; ant < N_ANTS; ant++) {
        for (int chan = 0; chan < N_CHANS; chan++) {
            for (int pol = 0; pol < N_POLS; pol++) {
                int chan_start = ((ant * N_CHANS + chan) * N_SAMPS + 0) * N_POLS + pol;
                for (int j = chan_start; j < chan_start + N_SAMPS * N_POLS; j = j + N_POLS) {
                    std::cout << h_block[j].real << " + " << h_block[j].imag << "i, ";
                }
                std::cout << std::endl;
            }
        }
    }

    std::cout << std::endl << std::endl;

    // Allocate memory on device
    comp_float_t *d_block;
    //float *d_output;
    cudaMalloc(&d_block, input_size);
    //cudaMalloc(&d_output, output_size);

    // Copy data to device
    cudaMemcpy(d_block, h_block, input_size, cudaMemcpyHostToDevice);

    // Launch kernel
    calculateSkArray(d_block,  N_ANTS, N_CHANS, N_SAMPS, N_POLS);

    // Copy result back to host
    cudaMemcpy(h_block, d_block, input_size, cudaMemcpyDeviceToHost);
    //cudaMemcpy(h_output, d_output, output_size, cudaMemcpyDeviceToHost);

    // print block after
    for (int ant = 0; ant < N_ANTS; ant++) {
        for (int chan = 0; chan < N_CHANS; chan++) {
            for (int pol = 0; pol < N_POLS; pol++) {
                int chan_start = ((ant * N_CHANS + chan) * N_SAMPS + 0) * N_POLS + pol;
                for (int j = chan_start; j < chan_start + N_SAMPS * N_POLS; j = j + N_POLS) {
                    std::cout << h_block[j].real << " + " << h_block[j].imag << "i, ";
                }
                std::cout << std::endl;
            }
        }
    }

    //std::cout << d_block[0] << std::endl;

    //for (int i = 0; i < 20; i++) {
        //std::cout << h_block[i * 8] << " " << h_block[i * 8 + 2] << " " << h_block[i * 8 + 4] << " " << h_block[i * 8 + 6] << " " << h_output[i] << std::endl;
        //std::cout << h_output[i] << std::endl;
    //}

    // Cleanup
    cudaFree(d_block);
    free(h_block);

    return 0;
}

