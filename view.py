import numpy as np
import matplotlib.pyplot as plt
import sys

brush_value = 255  # default value to paint
brush_size = 3  # radius of pixels painted


def draw_on_matrix(arr):
    # Ensure arr is integer type (uint8 preferred)
    if arr.dtype != np.uint8:
        arr[:] = np.clip(arr, 0, 255).astype(np.uint8)

    fig, ax = plt.subplots()
    img = ax.imshow(arr, cmap="gray", vmin=0, vmax=255)
    ax.set_title("Draw with left mouse button | Close to finish")
    plt.colorbar(img)

    drawing = [False]

    def paint(event):
        if not drawing[0]:
            return
        if event.xdata is None or event.ydata is None:
            return
        r = int(round(event.ydata))
        c = int(round(event.xdata))

        # draw a brush circle
        for dr in range(-brush_size, brush_size + 1):
            for dc in range(-brush_size, brush_size + 1):
                rr = r + dr
                cc = c + dc
                if 0 <= rr < arr.shape[0] and 0 <= cc < arr.shape[1]:
                    arr[rr, cc] = brush_value

        # clamp values IN PLACE
        np.clip(arr, 0, 255, out=arr)

        img.set_data(arr)
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


def main(npz_path):
    data = np.load(npz_path)
    keys = list(data.keys())

    print("\nArrays in NPZ:")
    for i, k in enumerate(keys):
        print(f"{i}: {k} shape={data[k].shape} dtype={data[k].dtype}")

    idx = int(input("\nEnter index of array to draw on: "))
    key = keys[idx]
    arr = data[key]

    print("\nClose the window when done drawing.")
    draw_on_matrix(arr)

    out = input("\nSave output as (default: drawn.npz): ").strip()
    if out == "":
        out = "drawn.npz"

    np.savez(out, **data)
    print(f"✅ Saved edited file as {out}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python draw_npz.py <file.npz>")
    else:
        main(sys.argv[1])
