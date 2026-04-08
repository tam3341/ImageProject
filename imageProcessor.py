import cv2

class imageProcessor:
    @staticmethod
    def apply_gaussian_blur(img, kernel_size=(5, 5), sigmaX=1.0):
        """
        1. Denoising: Gaussian Blur (Lecture 4)
        Optimal for Gaussian noise; preserves edges better than mean filter
        """
        if img is None: return None
        return cv2.GaussianBlur(img, kernel_size, sigmaX)

    @staticmethod
    def apply_clahe(img, clip_limit=2.0, tile_grid_size=(8, 8)):
        """
        2. Local Contrast: CLAHE (Lecture 3)
        Preserves local contrast while preventing over-enhancement in fridge lighting
        """
        if img is None: return None
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        cl = clahe.apply(l)
        enhanced = cv2.merge((cl, a, b))
        return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)

    @staticmethod
    def apply_unsharp_masking(img, kernel_size=(9, 9), sigmaX=10.0, k=1.5):
        """
        3. Edge Enhancement: Unsharp Masking (Lecture 4)
        Amplifies high-frequency details with tunable strength
        """
        if img is None: return None
        gaussian_blur_2 = cv2.GaussianBlur(img, kernel_size, sigmaX)
        return cv2.addWeighted(img, 1 + k, gaussian_blur_2, -k, 0)

    @staticmethod
    def enhance_image_pipeline(img_path, save_path=None):
        """
        Applies concepts from Lectures 3 & 4 to enhance images for YOLO training.
        """
        img = cv2.imread(img_path)
        if img is None: return None

        # 1. Denoising
        blur = imageProcessor.apply_gaussian_blur(img)

        # 2. Local Contrast
        enhanced_bgr = imageProcessor.apply_clahe(blur)

        # 3. Edge Enhancement
        final_img = imageProcessor.apply_unsharp_masking(enhanced_bgr)

        # Save or return
        if save_path:
            cv2.imwrite(save_path, final_img)
        return final_img