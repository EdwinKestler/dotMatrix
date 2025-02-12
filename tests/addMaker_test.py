import unittest
import numpy as np
import cv2
from dot_matrix_app.utils import dot_matrix_effect

class TestDotMatrixEffect(unittest.TestCase):
    def test_dot_matrix_on_synthetic_image(self):
        width, height = 200, 200
        synthetic_image = np.tile(np.linspace(0, 255, width, dtype=np.uint8), (height, 1))
        synthetic_image_bgr = cv2.cvtColor(synthetic_image, cv2.COLOR_GRAY2BGR)
        dot_size = 5
        output = dot_matrix_effect(synthetic_image_bgr, dot_size)
        self.assertEqual(output.shape, synthetic_image_bgr.shape)
        self.assertEqual(output.shape[2], 3)

if __name__ == '__main__':
    unittest.main()

