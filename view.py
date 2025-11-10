"""
View and interact with share files.
Display share metadata and pixel intensity values.
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os


def display_share_info(filepath):
    """Display information about a share file."""
    data = np.load(filepath, allow_pickle=False)
    
    print(f"\n{'='*60}")
    print(f"Share File: {os.path.basename(filepath)}")
    print(f"{'='*60}")
    
    # Check if it's new format (with metadata) or old format
    has_metadata = 'x' in data
    
    if has_metadata:
        # New format with metadata
        share_array = data['share']
        x = int(data['x'][0])
        prime = int(data['prime'][0])
        mode = str(data['mode'][0])
        original_shape = tuple(data['original_shape'])
        
        print(f"\nMetadata:")
        print(f"  X-coordinate: {x}")
        print(f"  Prime (field): {prime}")
        print(f"  Image mode: {mode}")
        print(f"  Original shape: {original_shape}")
    else:
        # Old format - only share array
        share_array = data['share']
        print(f"\n[WARNING] Old format (no metadata)")
        print(f"           Detected shape: {share_array.shape}")
        mode = 'grayscale' if share_array.ndim == 2 else 'rgb'
        print(f"           Inferred mode: {mode}")
    
    # Share array statistics
    print(f"\nShare Array Statistics:")
    print(f"  Shape: {share_array.shape}")
    print(f"  Dtype: {share_array.dtype}")
    print(f"  Min value: {np.min(share_array)}")
    print(f"  Max value: {np.max(share_array)}")
    print(f"  Mean value: {np.mean(share_array):.2f}")
    print(f"  Total elements: {share_array.size}")
    
    return share_array, mode


def visualize_share(share_array, mode, show_values=False):
    """Visualize the share array."""
    if mode == 'grayscale':
        # Display grayscale share
        fig, ax = plt.subplots(figsize=(10, 8))
        im = ax.imshow(share_array, cmap='gray', interpolation='nearest')
        ax.set_title('Share Visualization (Grayscale)')
        plt.colorbar(im, ax=ax, label='Pixel Intensity')
        
        # Show pixel values if image is small enough
        if show_values and share_array.shape[0] <= 20 and share_array.shape[1] <= 20:
            for i in range(share_array.shape[0]):
                for j in range(share_array.shape[1]):
                    text = ax.text(j, i, int(share_array[i, j]),
                                 ha="center", va="center", color="red", fontsize=8)
    else:
        # Display RGB share (show each channel separately)
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Combined RGB view (normalized for display)
        max_val = np.max(share_array)
        normalized = (share_array.astype(np.float32) / max_val * 255).astype(np.uint8)
        axes[0, 0].imshow(normalized)
        axes[0, 0].set_title('Combined RGB (normalized)')
        axes[0, 0].axis('off')
        
        # Individual channels
        channel_names = ['Red', 'Green', 'Blue']
        colors = ['Reds', 'Greens', 'Blues']
        for idx, (name, cmap) in enumerate(zip(channel_names, colors)):
            row = (idx + 1) // 2
            col = (idx + 1) % 2
            im = axes[row, col].imshow(share_array[:, :, idx], cmap=cmap, interpolation='nearest')
            axes[row, col].set_title(f'{name} Channel')
            plt.colorbar(im, ax=axes[row, col], label='Intensity')
            
            # Show pixel values if small enough
            if show_values and share_array.shape[0] <= 10 and share_array.shape[1] <= 10:
                for i in range(share_array.shape[0]):
                    for j in range(share_array.shape[1]):
                        text = axes[row, col].text(j, i, int(share_array[i, j, idx]),
                                                  ha="center", va="center", 
                                                  color="yellow", fontsize=6)
        
        plt.tight_layout()
    
    plt.show()


def draw_on_share(share_array, filepath):
    """Interactive drawing on share (from original view.py functionality)."""
    brush_value = 255
    brush_size = 3
    
    # For RGB, we'll modify all channels equally
    is_rgb = share_array.ndim == 3
    
    if is_rgb:
        # Use first channel for display but modify all
        display_array = share_array[:, :, 0].copy()
    else:
        display_array = share_array.copy()
    
    fig, ax = plt.subplots()
    img = ax.imshow(display_array, cmap='gray', vmin=0, vmax=np.max(display_array))
    ax.set_title("Draw with left mouse button | Close to finish")
    plt.colorbar(img)
    
    drawing = [False]
    
    def paint(event):
        if not drawing[0] or event.xdata is None or event.ydata is None:
            return
        
        r = int(round(event.ydata))
        c = int(round(event.xdata))
        
        # Draw a brush circle
        for dr in range(-brush_size, brush_size + 1):
            for dc in range(-brush_size, brush_size + 1):
                rr = r + dr
                cc = c + dc
                if 0 <= rr < share_array.shape[0] and 0 <= cc < share_array.shape[1]:
                    if is_rgb:
                        share_array[rr, cc, :] = brush_value
                        display_array[rr, cc] = brush_value
                    else:
                        share_array[rr, cc] = brush_value
                        display_array[rr, cc] = brush_value
        
        img.set_data(display_array)
        fig.canvas.draw_idle()
    
    def on_press(event):
        if event.button == 1:
            drawing[0] = True
            paint(event)
    
    def on_release(event):
        drawing[0] = False
    
    def on_move(event):
        paint(event)
    
    fig.canvas.mpl_connect("button_press_event", on_press)
    fig.canvas.mpl_connect("button_release_event", on_release)
    fig.canvas.mpl_connect("motion_notify_event", on_move)
    
    plt.show()
    
    # Save the modified share
    output = input("\nSave modified share as (Enter to skip): ").strip()
    if output:
        # Load original data and update share
        data = np.load(filepath, allow_pickle=False)
        save_dict = dict(data)
        save_dict['share'] = share_array
        np.savez_compressed(output, **save_dict)
        print(f"[SUCCESS] Saved modified share to: {output}")


def main(npz_path):
    """Main function for viewing shares."""
    if not os.path.exists(npz_path):
        print(f"[ERROR] File not found: {npz_path}")
        return
    
    # Display share information
    share_array, mode = display_share_info(npz_path)
    
    # Ask user what to do
    print(f"\n{'='*60}")
    print("Options:")
    print("  1. Visualize share")
    print("  2. Visualize share with pixel values (small images only)")
    print("  3. Interactive drawing mode")
    print("  4. Exit")
    print(f"{'='*60}")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == '1':
        visualize_share(share_array, mode, show_values=False)
    elif choice == '2':
        visualize_share(share_array, mode, show_values=True)
    elif choice == '3':
        draw_on_share(share_array, npz_path)
    elif choice == '4':
        print("Exiting...")
    else:
        print("Invalid choice. Exiting.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python view.py <share.npz>")
        print("\nExample:")
        print("  python view.py shares/share_1.npz")
    else:
        main(sys.argv[1])
