import unittest
import os
from PIL import Image
import image_processing

class ImageProcessingTests(unittest.TestCase):
    def setUp(self):
        """Set up a temporary directory for testing."""
        self.temp_dir = 'temp_test_dir'
        os.makedirs(self.temp_dir, exist_ok=True)
        self.test_img_path = os.path.join(self.temp_dir, 'test.jpg')
        test_img = Image.new('RGB', (100, 100), color='red')
        test_img.save(self.test_img_path)
        
        # Store original cache dir and set to our test dir
        self.original_cache_dir = image_processing.CACHE_DIR
        image_processing.CACHE_DIR = self.temp_dir
    
    def tearDown(self):
        """Clean up the temporary directory after tests."""
        image_processing.CACHE_DIR = self.original_cache_dir
        
        # Clean up any files that might still be there
        if os.path.exists(self.temp_dir):
            for file in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, file)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            os.rmdir(self.temp_dir)
    
    def test_resize_image(self):
        """Test that resize_image correctly resizes an image."""
        width, height = 50, 60
        result = image_processing.resize_image(self.test_img_path, width, height)
        
        assert os.path.exists(result)
        resized_img = Image.open(result)
        assert resized_img.size == (width, height)
    
    def test_clear_cache_on_restart(self):
        """Test that clear_cache_on_restart removes all files in the cache directory."""
        # Create some test files in the temp directory
        test_files = ['file1.jpg', 'file2.jpg', 'file3.jpg']
        for filename in test_files:
            with open(os.path.join(self.temp_dir, filename), 'w') as f:
                f.write('test content')
        
        # Run the function we're testing
        image_processing.clear_cache_on_restart()
        
        # Verify that all files were removed
        remaining_files = os.listdir(self.temp_dir)
        assert len(remaining_files) == 0, f"Files remaining: {remaining_files}"

if __name__ == '__main__':
    unittest.main()