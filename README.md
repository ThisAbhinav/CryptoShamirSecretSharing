```
python shamir_image_shares.py split input.png shares --n 5 --k 3

python shamir_image_shares.py reconstruct recovered.png shares/share_1.npz shares/share_3.npz shares/share_5.npz

python view.py shares/share_1.npz

python verify.py input.png recovered.png
```# CryptoShamirSecretSharing
