import os
import open3d as o3d
import numpy as np
import shutil

class PointCloudDownsampler:
    def __init__(self, input_dir, output_dir, temp_dir, N, voxel_start=0.0001, voxel_step=0.0005):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.temp_dir = temp_dir
        self.N = N
        self.voxel_start = voxel_start
        self.voxel_step = voxel_step

        # Ensure output and temp directories exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)

    def downsample_point_cloud(self, point_cloud, voxel_size):
        return point_cloud.voxel_down_sample(voxel_size)

    def process_point_clouds(self):
        for filename in os.listdir(self.input_dir):
            if filename.endswith(".pcd") or filename.endswith(".ply"):
                file_path = os.path.join(self.input_dir, filename)
                pcd = o3d.io.read_point_cloud(file_path)
                num_points = len(pcd.points)

                voxel_size = self.voxel_start
                best_voxel_size = None
                best_num_points = num_points

                print(f"Processing {filename} with {num_points} points")

                while True:
                    downsampled_pcd = self.downsample_point_cloud(pcd, voxel_size)
                    downsampled_num_points = len(downsampled_pcd.points)

                    print(f"Trying voxel size: {voxel_size:.5f} -> {downsampled_num_points} points")

                    if downsampled_num_points < self.N:
                        if best_num_points > self.N:
                            print(f"Found optimal voxel size: {best_voxel_size:.5f} with {best_num_points} points")
                            break
                        print(f"Breaking at voxel size {voxel_size:.5f} with {downsampled_num_points} points")
                        break
                    else:
                        best_voxel_size = voxel_size
                        best_num_points = downsampled_num_points

                    voxel_size += self.voxel_step

                if best_voxel_size:
                    optimal_pcd = self.downsample_point_cloud(pcd, best_voxel_size)
                    temp_path = os.path.join(self.temp_dir, filename)
                    o3d.io.write_point_cloud(temp_path, optimal_pcd)
                    print(f"Temporarily saved {filename} with {len(optimal_pcd.points)} points to {self.temp_dir}")

                print("-" * 50)

    def random_downsample_point_cloud(self, pcd, target_size):
        num_points = len(pcd.points)
        if num_points <= target_size:
            print(f"No downsampling needed. Point cloud has {num_points} points, which is less than or equal to {target_size}.")
            return pcd

        indices = np.random.choice(num_points, target_size, replace=False)
        downsampled_pcd = pcd.select_by_index(indices)

        return downsampled_pcd

    def downsample_all_to_target_size(self):
        for filename in os.listdir(self.temp_dir):
            if filename.endswith(".pcd") or filename.endswith(".ply"):
                file_path = os.path.join(self.temp_dir, filename)
                try:
                    pcd = o3d.io.read_point_cloud(file_path)
                    original_size = len(pcd.points)

                    print(f"Processing {filename}: Original size = {original_size} points")

                    downsampled_pcd = self.random_downsample_point_cloud(pcd, self.N)
                    downsampled_size = len(downsampled_pcd.points)

                    output_path = os.path.join(self.output_dir, f"{filename}")
                    o3d.io.write_point_cloud(output_path, downsampled_pcd)

                    print(f"Downsampled {filename}: New size = {downsampled_size} points")
                    print(f"Saved downsampled point cloud to {output_path}")
                    print("-" * 50)

                except Exception as e:
                    print(f"Failed to process {filename}: {e}")

        # Clean up the temp directory
        shutil.rmtree(self.temp_dir)
        print(f"Temporary files in {self.temp_dir} have been deleted.")


input_dir = "/path/to/input/directory"
output_dir = "/path/to/output/directory"
temp_dir = "/path/to/temp/directory"  
N = 50000  # Target number of points

processor = PointCloudDownsampler(input_dir, output_dir, temp_dir, N)
processor.process_point_clouds()
processor.downsample_all_to_target_size()

