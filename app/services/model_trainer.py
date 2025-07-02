"""
3D扩散模型训练服务
"""

import os
import json
import logging
import torch
import numpy as np
from datetime import datetime, timezone
from typing import Dict, List, Optional
from diffusers import DDPMScheduler, UNet3DConditionModel
from transformers import AutoTokenizer, AutoModel

from app import db
from app.models.training_job import TrainingJob
from app.models.map_data import MapData
from app.models.annotation import Annotation

logger = logging.getLogger(__name__)

class ModelTrainer:
    """3D扩散模型训练器"""

    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.tokenizer = None
        self.text_encoder = None

    def setup_text_encoder(self):
        """设置文本编码器"""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
            self.text_encoder = AutoModel.from_pretrained("bert-base-uncased")
            self.text_encoder.to(self.device)
        except Exception as e:
            logger.error(f"Failed to setup text encoder: {e}")

    @staticmethod
    def create_training_job(config: Dict) -> TrainingJob:
        """创建训练任务"""
        job = TrainingJob(
            name=config['name'],
            description=config.get('description', ''),
            model_type=config.get('model_type', 'diffusion'),
            total_epochs=config.get('epochs', 100)
        )
        job.set_training_config(config)

        db.session.add(job)
        db.session.commit()

        return job

    def prepare_training_data(self, job_id: int) -> bool:
        """准备训练数据"""
        try:
            job = TrainingJob.query.get(job_id)
            if not job:
                return False

            # 获取所有已标注的地图数据
            map_data_list = MapData.query.filter_by(is_parsed=True).all()
            training_samples = []

            for map_data in map_data_list:
                annotations = Annotation.query.filter_by(map_data_id=map_data.id).all()

                for annotation in annotations:
                    # 提取标注区域的3D数据
                    sample = self._extract_training_sample(map_data, annotation)
                    if sample:
                        training_samples.append(sample)

            # 保存训练数据
            from flask import current_app
            data_dir = current_app.config.get('TRAINING_DATA_DIR', 'training_data')
            os.makedirs(data_dir, exist_ok=True)

            train_file = os.path.join(data_dir, f'training_data_{job_id}.json')
            with open(train_file, 'w') as f:
                json.dump(training_samples, f)

            job.training_data_path = train_file
            db.session.commit()

            logger.info(f"Prepared {len(training_samples)} training samples for job {job_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to prepare training data: {e}")
            return False

    def _extract_training_sample(self, map_data: MapData, annotation: Annotation) -> Optional[Dict]:
        """提取训练样本"""
        try:
            # 加载解析后的地图数据
            from flask import current_app
            cache_dir = current_app.config.get('MODEL_CACHE_DIR', 'cache')
            data_file = os.path.join(cache_dir, f'map_data_{map_data.id}.json')

            if not os.path.exists(data_file):
                return None

            with open(data_file, 'r') as f:
                parsed_data = json.load(f)

            # 提取标注区域内的方块
            blocks = parsed_data.get('blocks', [])
            region_blocks = []

            for block in blocks:
                if (annotation.min_x <= block['x'] <= annotation.max_x and
                    annotation.min_y <= block['y'] <= annotation.max_y and
                    annotation.min_z <= block['z'] <= annotation.max_z):
                    region_blocks.append(block)

            if not region_blocks:
                return None

            # 转换为3D张量格式
            voxel_data = self._blocks_to_voxel(region_blocks, annotation)

            return {
                'voxel_data': voxel_data.tolist(),
                'label': annotation.label,
                'description': annotation.description,
                'bbox': {
                    'min': [annotation.min_x, annotation.min_y, annotation.min_z],
                    'max': [annotation.max_x, annotation.max_y, annotation.max_z]
                }
            }

        except Exception as e:
            logger.error(f"Failed to extract training sample: {e}")
            return None

    @staticmethod
    def _blocks_to_voxel(blocks: List[Dict], annotation: Annotation) -> np.ndarray:
        """将方块数据转换为体素张量"""
        # 计算区域大小
        width = annotation.max_x - annotation.min_x + 1
        height = annotation.max_y - annotation.min_y + 1
        depth = annotation.max_z - annotation.min_z + 1

        # 创建体素数组
        voxel = np.zeros((width, height, depth), dtype=np.int32)

        # 填充方块数据
        for block in blocks:
            x = block['x'] - annotation.min_x
            y = block['y'] - annotation.min_y
            z = block['z'] - annotation.min_z

            if 0 <= x < width and 0 <= y < height and 0 <= z < depth:
                voxel[x, y, z] = block['numeric_id']

        return voxel

    def train_model(self, job_id: int):
        """训练模型"""
        try:
            job = TrainingJob.query.get(job_id)
            if not job:
                logger.error(f"Training job not found: {job_id}")
                return

            # 更新状态
            job.status = 'running'
            job.started_at = datetime.now(timezone.utc)
            db.session.commit()

            # 加载训练数据
            training_data = self._load_training_data(job.training_data_path)
            if not training_data:
                raise ValueError("No training data available")

            # 创建模型
            model = self._create_model(job.get_training_config())
            optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)
            scheduler = DDPMScheduler(num_train_timesteps=1000)

            # 训练循环
            for epoch in range(job.total_epochs):
                epoch_loss = self._train_epoch(model, optimizer, scheduler, training_data)

                # 更新进度
                job.update_progress(epoch + 1, train_loss=epoch_loss)
                db.session.commit()

                logger.info(f"Epoch {epoch + 1}/{job.total_epochs}, Loss: {epoch_loss:.4f}")

                # 保存检查点
                if (epoch + 1) % 10 == 0:
                    self._save_checkpoint(model, job_id, epoch + 1)

            # 保存最终模型
            model_path = self._save_final_model(model, job_id)

            # 更新任务状态
            job.status = 'completed'
            job.completed_at = datetime.now(timezone.utc)
            job.model_path = model_path
            db.session.commit()

            logger.info(f"Training completed for job {job_id}")

        except Exception as e:
            logger.error(f"Training failed for job {job_id}: {e}")

            # 更新错误状态
            job = TrainingJob.query.get(job_id)
            if job:
                job.status = 'failed'
                job.error_message = str(e)
                db.session.commit()

    @staticmethod
    def _load_training_data(data_path: str) -> List[Dict]:
        """加载训练数据"""
        try:
            with open(data_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load training data: {e}")
            return []

    def _create_model(self, config: Dict):
        """创建3D UNet模型"""
        model = UNet3DConditionModel(
            sample_size=config.get('sample_size', 32),
            in_channels=config.get('in_channels', 1),
            out_channels=config.get('out_channels', 1),
            layers_per_block=config.get('layers_per_block', 2),
            block_out_channels=config.get('block_out_channels', [128, 256, 512, 512]),
            down_block_types=config.get('down_block_types', [
                "CrossAttnDownBlock3D",
                "CrossAttnDownBlock3D",
                "CrossAttnDownBlock3D",
                "DownBlock3D"
            ]),
            up_block_types=config.get('up_block_types', [
                "UpBlock3D",
                "CrossAttnUpBlock3D",
                "CrossAttnUpBlock3D",
                "CrossAttnUpBlock3D"
            ]),
            cross_attention_dim=config.get('cross_attention_dim', 768)
        )

        return model.to(self.device)

    def _train_epoch(self, model, optimizer, scheduler, training_data: List[Dict]) -> float:
        """训练一个epoch"""
        model.train()
        total_loss = 0
        num_batches = 0

        for sample in training_data:
            try:
                # 准备数据
                voxel_data = torch.tensor(sample['voxel_data'], dtype=torch.float32).unsqueeze(0).unsqueeze(0)
                voxel_data = voxel_data.to(self.device)

                # 编码文本
                text_embeddings = self._encode_text(sample['description'])

                # 添加噪声
                noise = torch.randn_like(voxel_data)
                timesteps = torch.randint(0, scheduler.config.num_train_timesteps, (1,), device=self.device)
                noisy_voxels = scheduler.add_noise(voxel_data, noise, timesteps)

                # 前向传播
                noise_pred = model(noisy_voxels, timesteps, text_embeddings).sample

                # 计算损失
                loss = torch.nn.functional.mse_loss(noise_pred, noise)

                # 反向传播
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                total_loss += loss.item()
                num_batches += 1

            except Exception as e:
                logger.warning(f"Failed to process sample: {e}")
                continue

        return total_loss / max(num_batches, 1)

    def _encode_text(self, text: str) -> torch.Tensor:
        """编码文本描述"""
        if not self.tokenizer or not self.text_encoder:
            self.setup_text_encoder()

        try:
            inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.text_encoder(**inputs)
                return outputs.last_hidden_state

        except Exception as e:
            logger.error(f"Failed to encode text: {e}")
            # 返回零张量作为后备
            return torch.zeros(1, 512, 768, device=self.device)

    @staticmethod
    def _save_checkpoint(model, job_id: int, epoch: int):
        """保存检查点"""
        try:
            from flask import current_app
            cache_dir = current_app.config.get('MODEL_CACHE_DIR', 'cache')
            checkpoint_dir = os.path.join(cache_dir, f'job_{job_id}_checkpoints')
            os.makedirs(checkpoint_dir, exist_ok=True)

            checkpoint_path = os.path.join(checkpoint_dir, f'checkpoint_epoch_{epoch}.pt')
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'job_id': job_id
            }, checkpoint_path)

            # 更新数据库
            job = TrainingJob.query.get(job_id)
            if job:
                job.checkpoint_path = checkpoint_path
                db.session.commit()

        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")

    @staticmethod
    def _save_final_model(model, job_id: int) -> str:
        """保存最终模型"""
        try:
            from flask import current_app
            cache_dir = current_app.config.get('MODEL_CACHE_DIR', 'cache')
            model_dir = os.path.join(cache_dir, f'job_{job_id}_model')
            os.makedirs(model_dir, exist_ok=True)

            model_path = os.path.join(model_dir, 'final_model.pt')
            torch.save(model.state_dict(), model_path)

            return model_path

        except Exception as e:
            logger.error(f"Failed to save final model: {e}")
            return ""
