import cv2
import numpy as np
import open3d as o3d

# 画像の読み込み
imgL = cv2.imread("sample/left.jpg", cv2.IMREAD_GRAYSCALE)  # 左の画像
imgR = cv2.imread("sample/right.jpg", cv2.IMREAD_GRAYSCALE)  # 右の画像

# ステレオマッチングオブジェクトの作成
stereo = cv2.StereoBM_create(numDisparities=16, blockSize=15)

# 深度マップの計算
disparity = stereo.compute(imgL, imgR).astype(np.float32) / 16.0

# Open3Dで点群を生成
h, w = disparity.shape
focal_length = 0.8 * w  # 仮の焦点距離
Q = np.float32(
    [
        [1, 0, 0, -0.5 * w],
        [0, -1, 0, 0.5 * h],  # 上下反転
        [0, 0, 0, -focal_length],
        [0, 0, 1, 0],
    ]
)
points = cv2.reprojectImageTo3D(disparity, Q)
colors = cv2.cvtColor(cv2.imread("sample/left.jpg"), cv2.COLOR_BGR2RGB)
mask = disparity > disparity.min()
out_points = points[mask]
out_colors = colors[mask]

# Open3Dの点群オブジェクトを作成
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(out_points)
pcd.colors = o3d.utility.Vector3dVector(out_colors / 255.0)

# 点群の表示
o3d.visualization.draw_geometries([pcd])
