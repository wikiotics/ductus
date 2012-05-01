import pytest

from ductus.resource import SizeTooLargeError, check_resource_size, calculate_hash, ResourceDatabase

some_data = 'aerfdnjdfgjkdsgkjdfsgjkdfsgds'

def test_check_resource_size():
    assert tuple(check_resource_size(iter(some_data), len(some_data))) is not None
    with pytest.raises(SizeTooLargeError):
        tuple(check_resource_size(iter(some_data), len(some_data) - 1))

def test_is_valid_urn():
    assert ResourceDatabase.is_valid_urn('urn:sha384:35F_NeGhyCPV0sZ-3dS3vCB9ZavpGLOszmTWjMRlso1sVH3MSYy796PqCmjCp9zs')
    assert not ResourceDatabase.is_valid_urn('urn:sha384:35F_NeGhyCPV0sZ-3dS3vCB9ZavpGLOszmTWjMRlso1sVH3MSYy796PqCmjCp9z')
    assert not ResourceDatabase.is_valid_urn('url:sha384:35F_NeGhyCPV0sZ-3dS3vCB9ZavpGLOszmTWjMRlso1sVH3MSYy796PqCmjCp9zs')
    assert not ResourceDatabase.is_valid_urn('urn:sha383:35F_NeGhyCPV0sZ-3dS3vCB9ZavpGLOszmTWjMRlso1sVH3MSYy796PqCmjCp9zs')
    assert not ResourceDatabase.is_valid_urn('urn:sha384::35F_NeGhyCPV0sZ-3dS3vCB9ZavpGLOszmTWjMRlso1sVH3MSYy796PqCmjCp9zs')
    assert not ResourceDatabase.is_valid_urn('urn::35F_NeGhyCPV0sZ-3dS3vCB9ZavpGLOszmTWjMRlso1sVH3MSYy796PqCmjCp9zs')
    assert not ResourceDatabase.is_valid_urn('urn:35F_NeGhyCPV0sZ-3dS3vCB9ZavpGLOszmTWjMRlso1sVH3MSYy796PqCmjCp9zs')
