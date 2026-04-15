import cv2
from ultralytics import YOLO

class imageProcessor:
    @staticmethod
    def apply_gaussian_blur(img, kernel_size=(3, 3), sigmaX=0.4):
        if img is None: return None
        return cv2.GaussianBlur(img, kernel_size, sigmaX)

    @staticmethod
    def apply_median_blur(img, kernel_size=7):
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
    def detect_ingrediants(img, model_weights='best.pt'):
        inference_model = YOLO(model_weights)
        results = inference_model.predict(img, conf=0.25)[0]
        
        plotted_img = results.plot()
        
        detected_items = []
        for box in results.boxes:
            class_id = int(box.cls[0].item())
            class_name = results.names[class_id]
            confidence = float(box.conf[0].item())
            detected_items.append({"name": class_name, "confidence": confidence})
            
        return plotted_img, detected_items
        
    @staticmethod
    def enhance_image_pipeline(img, save_path=None):
        denoised = imageProcessor.apply_median_blur(img)
        blur = imageProcessor.apply_gaussian_blur(denoised)
        enhanced_bgr = imageProcessor.apply_clahe(blur)
        final_img = imageProcessor.apply_unsharp_masking(enhanced_bgr)
        if save_path:
            cv2.imwrite(save_path, final_img)
        return final_img
