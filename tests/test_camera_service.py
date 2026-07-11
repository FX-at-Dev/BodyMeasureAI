from src.services.camera_service import CameraService


def test_camera_creation():

    camera = CameraService()

    assert camera is not None
