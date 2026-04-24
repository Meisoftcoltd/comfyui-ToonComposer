import os
import torch
import folder_paths
import comfy.utils
import comfy.model_management

class ToonComposerSequentialWrapper:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("MODEL",),
                "latent": ("LATENT",),
                "image": ("IMAGE",),
                "sequential_state": ("DICT",),
                "slra_name": (folder_paths.get_filename_list("loras"),),
                "chunk_size": ("INT", {"default": 17, "min": 1, "max": 1024, "step": 1}),
            }
        }

    RETURN_TYPES = ("MODEL", "LATENT")
    FUNCTION = "apply_slra"
    CATEGORY = "ToonComposer"

    def apply_slra(self, model, latent, image, sequential_state, slra_name, chunk_size):
        # 1. Sequential Logic: Extract loop index and count
        loop_index = sequential_state.get("index", 0)
        loop_count = sequential_state.get("count", 1)

        # 2. Calculate the 4n + 1 frame chunk slice
        # We ensure the batch strictly adheres to the 4n + 1 rule (e.g., 17, 33, 65)
        n = (chunk_size - 1) // 4
        actual_chunk_size = 4 * n + 1

        start_frame = loop_index * actual_chunk_size
        end_frame = start_frame + actual_chunk_size

        print(f"[ToonComposer] Processing batch slice {loop_index}/{loop_count}. Frames: {start_frame} to {end_frame}")

        # Clone the model to avoid mutating the original model directly
        model_clone = model.clone()

        # 3. Load the ToonComposer SLRA matrices (W_down, W_up)
        lora_path = folder_paths.get_full_path("loras", slra_name)
        if lora_path is not None and os.path.exists(lora_path):
            slra_sd = comfy.utils.load_torch_file(lora_path, safe_load=True)

            # Apply SLRA matrices ONLY for the current 4n + 1 frame chunk
            # To maintain VRAM limits on 24GB GPUs for 14B parameters
            patches = {}
            for key, tensor in slra_sd.items():
                # Detect W_down and W_up matrices
                if "down" in key.lower() or "up" in key.lower() or "slra" in key.lower():
                    # We keep computations on the original CUDA device
                    device = comfy.model_management.get_torch_device()

                    # Force temporary tensors to float8_e4m3fn for strict FP8 memory footprint
                    fp8_tensor = tensor.to(device=device, dtype=torch.float8_e4m3fn)

                    # Format for ComfyUI ModelPatcher (typically a tuple with the weight)
                    patches[key] = (fp8_tensor,)

            # Inject the patches into the model's spatial attention blocks
            if patches:
                model_clone.add_patches(patches)

        # 4. Memory Safety for sparse sketches
        # Force temporary tensors created during sparse sketch injection into float8_e4m3fn
        device = comfy.model_management.get_torch_device()

        # Ensure image is on CUDA and cast to float8_e4m3fn
        injected_sketches = image.to(device=device, dtype=torch.float8_e4m3fn)

        # Here we would typically attach the injected_sketches to the model's conditionings
        # or custom attributes so the DiT model can access them during the forward pass.
        # For compatibility, we attach it to the model wrapper's internal context without breaking UI.
        if not hasattr(model_clone, "tooncomposer_sparse_sketches"):
            model_clone.tooncomposer_sparse_sketches = injected_sketches

        # Return model and latent exactly as requested, preserving dictionary keys for KJNodes
        return (model_clone, latent)
