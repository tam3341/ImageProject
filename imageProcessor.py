import cv2
import numpy as np
from ultralytics import YOLO


class imageProcessor:

    @staticmethod
    def is_noisy(img, threshold=15.0):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        smoothed = cv2.medianBlur(gray, 5)
        noise_diff = cv2.absdiff(gray, smoothed)
        noise_level = np.std(noise_diff)
        return noise_level > threshold, noise_level

    @staticmethod
    def is_blurry(img, threshold=100.0):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        return laplacian_var < threshold, laplacian_var

    @staticmethod
    def needs_contrast_boost(img, threshold=45.0):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        contrast_level = np.std(gray)
        return contrast_level < threshold, contrast_level

    @staticmethod
    def apply_gaussian_blur(img, kernel_size=(3, 3), sigmaX=0.4):
        if img is None: return None
        return cv2.GaussianBlur(img, kernel_size, sigmaX)

    @staticmethod
    def apply_median_blur(img, kernel_size=5):
        if img is None: return None
        return cv2.medianBlur(img, kernel_size)

    @staticmethod
    def apply_clahe(img, clip_limit=1.2, tile_grid_size=(8, 8)):
        if img is None: return None
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        cl = clahe.apply(l)
        enhanced = cv2.merge((cl, a, b))
        return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)

    @staticmethod
    def apply_unsharp_masking(img, kernel_size=(9, 9), sigmaX=2.0, k=0.5):
        if img is None: return None
        gaussian_blur_2 = cv2.GaussianBlur(img, kernel_size, sigmaX)
        return cv2.addWeighted(img, 1 + k, gaussian_blur_2, -k, 0)

    @staticmethod
    def enhance_image_pipeline(img, save_path=None):
        if img is None: return None, []

        current_img = img.copy()
        logs = []
        logs.append("--- Analyzing Image ---")

        noisy, noise_val = imageProcessor.is_noisy(current_img)
        if noisy:
            logs.append(f"[+] High noise detected ({noise_val:.2f}). Applying Median Blur.")
            current_img = imageProcessor.apply_median_blur(current_img)
        else:
            logs.append(f"[-] Image is clean ({noise_val:.2f}). Skipping Median Blur.")

        low_contrast, contrast_val = imageProcessor.needs_contrast_boost(current_img)
        if low_contrast:
            logs.append(f"[+] Low contrast detected ({contrast_val:.2f}). Applying CLAHE.")
            current_img = imageProcessor.apply_clahe(current_img)
        else:
            logs.append(f"[-] Contrast is good ({contrast_val:.2f}). Skipping CLAHE.")

        blurry, blur_val = imageProcessor.is_blurry(current_img)
        if blurry:
            logs.append(f"[+] Blur detected (Laplacian Var: {blur_val:.2f}). Applying Unsharp Mask.")
            current_img = imageProcessor.apply_unsharp_masking(current_img)
        else:
            logs.append(f"[-] Image is sharp (Laplacian Var: {blur_val:.2f}). Skipping Sharpening.")

        logs.append("-----------------------")

        if save_path:
            cv2.imwrite(save_path, current_img)

        return current_img, logs

    @staticmethod
    def detect_ingredients(img, model_weights='best.pt'):
        inference_model = YOLO(model_weights)
        results = inference_model.predict(img, conf=0.25)[0]

        plotted_img = results.plot()

        detected_items = []
        for box in results.boxes:
            class_id = int(box.cls[0].item())
            class_name = results.names[class_id]
            confidence = float(box.conf[0].item())
            detected_items.append({"name": class_name, "confidence": round(confidence, 2)})

        return plotted_img, detected_items