import requests
import unittest
import base64
from io import BytesIO
from PIL import Image
import os

class LogoCreatorAPITest(unittest.TestCase):
    def setUp(self):
        self.base_url = "https://dd6942c8-8fcb-4e8a-b744-ec9990d94c7f.preview.emergentagent.com"
        
    def test_api_root(self):
        """Test the root API endpoint"""
        response = requests.get(f"{self.base_url}/api")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Logo Creator API"})
        print("✅ Root API endpoint test passed")

    def test_generate_logo_valid_prompt(self):
        """Test logo generation with valid prompt"""
        data = {
            "prompt": "A modern tech startup logo with blue and green elements",
            "size": "1024x1024"
        }
        response = requests.post(f"{self.base_url}/api/generate-logo", json=data)
        self.assertEqual(response.status_code, 200)
        
        response_data = response.json()
        self.assertTrue(response_data["success"])
        self.assertIn("image", response_data)
        self.assertIn("filename", response_data)
        
        # Verify the image data is valid base64
        try:
            image_data = base64.b64decode(response_data["image"])
            img = Image.open(BytesIO(image_data))
            self.assertTrue(img.size == (1024, 1024))
        except Exception as e:
            self.fail(f"Invalid image data: {str(e)}")
        
        print("✅ Logo generation test passed")

    def test_generate_logo_empty_prompt(self):
        """Test logo generation with empty prompt"""
        data = {
            "prompt": "",
            "size": "1024x1024"
        }
        response = requests.post(f"{self.base_url}/api/generate-logo", json=data)
        self.assertEqual(response.status_code, 400)
        print("✅ Empty prompt validation test passed")

    def test_get_nonexistent_image(self):
        """Test getting a non-existent image"""
        response = requests.get(f"{self.base_url}/api/image/nonexistent.png")
        self.assertEqual(response.status_code, 404)
        print("✅ Non-existent image test passed")

if __name__ == '__main__':
    unittest.main(verbosity=2)
