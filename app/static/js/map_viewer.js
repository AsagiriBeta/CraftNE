/**
 * CraftNE 3D地图查看器
 * 基于Three.js的Minecraft地图可视化
 */

class MapViewer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.mapData = null;
        this.blockMeshes = [];
        this.annotations = [];
        
        this.init();
    }
    
    init() {
        // 创建场景
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x87CEEB); // 天空蓝
        
        // 创建相机
        this.camera = new THREE.PerspectiveCamera(
            75,
            this.container.clientWidth / this.container.clientHeight,
            0.1,
            1000
        );
        this.camera.position.set(50, 50, 50);
        
        // 创建渲染器
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.container.appendChild(this.renderer.domElement);
        
        // 添加控制器
        this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        
        // 添加光源
        this.setupLighting();
        
        // 监听窗口大小变化
        window.addEventListener('resize', () => this.onWindowResize());
        
        // 开始渲染循环
        this.animate();
    }
    
    setupLighting() {
        // 环境光
        const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
        this.scene.add(ambientLight);
        
        // 方向光（太阳光）
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(50, 100, 50);
        directionalLight.castShadow = true;
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        this.scene.add(directionalLight);
    }
    
    async loadMap(mapId) {
        try {
            // 显示加载提示
            this.showLoadingMessage('Loading map data...');
            
            // 获取地图数据
            const response = await fetch(`/upload/api/maps/${mapId}`);
            const mapData = await response.json();
            
            if (!mapData.is_parsed) {
                this.showMessage('Map is not parsed yet', 'warning');
                return;
            }
            
            this.mapData = mapData;
            
            // 加载方块数据
            await this.loadBlocks(mapId);
            
            // 加载标注数据
            await this.loadAnnotations(mapId);
            
            // 调整相机位置
            this.fitCameraToMap();
            
            this.hideLoadingMessage();
            
        } catch (error) {
            console.error('Error loading map:', error);
            this.showMessage('Failed to load map', 'error');
        }
    }
    
    async loadBlocks(mapId) {
        try {
            const response = await fetch(`/api/maps/${mapId}/blocks`);
            const blocks = await response.json();
            
            this.showLoadingMessage(`Loading ${blocks.length} blocks...`);
            
            // 清除现有方块
            this.clearBlocks();
            
            // 创建方块材质
            const materials = this.createBlockMaterials();
            
            // 批量创建方块（优化性能）
            const instancedMeshes = new Map();
            
            blocks.forEach((block, index) => {
                if (index % 1000 === 0) {
                    this.showLoadingMessage(`Loading blocks: ${index}/${blocks.length}`);
                }
                
                const blockType = block.block_type;
                
                if (!instancedMeshes.has(blockType)) {
                    // 创建实例化几何体
                    const geometry = new THREE.BoxGeometry(1, 1, 1);
                    const material = materials.get(blockType) || materials.get('default');
                    
                    // 估算该类型方块数量
                    const count = blocks.filter(b => b.block_type === blockType).length;
                    const instancedMesh = new THREE.InstancedMesh(geometry, material, count);
                    instancedMesh.castShadow = true;
                    instancedMesh.receiveShadow = true;
                    
                    instancedMeshes.set(blockType, {
                        mesh: instancedMesh,
                        index: 0
                    });
                    
                    this.scene.add(instancedMesh);
                }
                
                // 设置实例位置
                const instance = instancedMeshes.get(blockType);
                const matrix = new THREE.Matrix4();
                matrix.setPosition(block.x, block.y, block.z);
                instance.mesh.setMatrixAt(instance.index, matrix);
                instance.index++;
            });
            
            // 更新实例化网格
            instancedMeshes.forEach(instance => {
                instance.mesh.instanceMatrix.needsUpdate = true;
            });
            
            this.blockMeshes = Array.from(instancedMeshes.values()).map(instance => instance.mesh);

        } catch (error) {
            console.error('Error loading blocks:', error);
            this.showMessage('Failed to load blocks', 'error');
        }
    }
    
    createBlockMaterials() {
        const materials = new Map();
        
        // 基础材质配置
        const materialConfigs = {
            'minecraft:stone': { color: 0x7F7F7F },
            'minecraft:grass_block': { color: 0x7CBD6B },
            'minecraft:dirt': { color: 0x8B4513 },
            'minecraft:cobblestone': { color: 0x6F6F6F },
            'minecraft:oak_planks': { color: 0xC4A570 },
            'minecraft:oak_log': { color: 0x8B4513 },
            'minecraft:oak_leaves': { color: 0x228B22, transparent: true, opacity: 0.8 },
            'minecraft:water': { color: 0x4169E1, transparent: true, opacity: 0.6 },
            'minecraft:lava': { color: 0xFF4500, emissive: 0xFF4500 },
            'default': { color: 0xCCCCCC }
        };
        
        // 创建材质
        Object.entries(materialConfigs).forEach(([blockType, config]) => {
            const material = new THREE.MeshLambertMaterial({
                color: config.color,
                transparent: config.transparent || false,
                opacity: config.opacity || 1.0
            });

            if (config.emissive) {
                material.emissive.setHex(config.emissive);
                material.emissiveIntensity = 0.3;
            }

            materials.set(blockType, material);
        });
        
        return materials;
    }
    
    async loadAnnotations(mapId) {
        try {
            const response = await fetch(`/annotation/api/annotations/${mapId}`);
            const annotations = await response.json();
            
            this.annotations = annotations;
            this.renderAnnotations();

        } catch (error) {
            console.error('Error loading annotations:', error);
        }
    }
    
    renderAnnotations() {
        // 清除现有标注
        this.scene.children.filter(child => child.userData.isAnnotation).forEach(child => {
            this.scene.remove(child);
        });
        
        // 渲染新标注
        this.annotations.forEach(annotation => {
            const coords = JSON.parse(annotation.coordinates);

            // 创建标注框
            const geometry = new THREE.BoxGeometry(
                coords.width || 1,
                coords.height || 1,
                coords.depth || 1
            );

            const material = new THREE.MeshBasicMaterial({
                color: 0xFF0000,
                wireframe: true,
                transparent: true,
                opacity: 0.5
            });

            const annotationMesh = new THREE.Mesh(geometry, material);
            annotationMesh.position.set(coords.x, coords.y, coords.z);
            annotationMesh.userData.isAnnotation = true;
            annotationMesh.userData.annotation = annotation;

            this.scene.add(annotationMesh);
        });
    }
    
    clearBlocks() {
        // 移除所有方块网格
        this.blockMeshes.forEach(mesh => {
            this.scene.remove(mesh);
            mesh.geometry.dispose();
            mesh.material.dispose();
        });
        this.blockMeshes = [];
    }
    
    fitCameraToMap() {
        if (!this.mapData || !this.blockMeshes.length) return;

        // 计算场景边界
        const box = new THREE.Box3();
        this.blockMeshes.forEach(mesh => {
            box.expandByObject(mesh);
        });

        const center = box.getCenter(new THREE.Vector3());
        const size = box.getSize(new THREE.Vector3());

        // 调整相机位置
        const maxDim = Math.max(size.x, size.y, size.z);
        const fov = this.camera.fov * (Math.PI / 180);
        let cameraZ = Math.abs(maxDim / 2 / Math.tan(fov / 2));

        cameraZ *= 1.5; // 添加一些边距

        this.camera.position.set(center.x + cameraZ, center.y + cameraZ, center.z + cameraZ);
        this.camera.lookAt(center);

        // 更新控制器目标
        this.controls.target.copy(center);
        this.controls.update();
    }
    
    onWindowResize() {
        this.camera.aspect = this.container.clientWidth / this.container.clientHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
    }
    
    animate() {
        requestAnimationFrame(() => this.animate());
        
        this.controls.update();
        this.renderer.render(this.scene, this.camera);
    }
    
    showLoadingMessage(message) {
        let loadingDiv = document.getElementById('map-loading');
        if (!loadingDiv) {
            loadingDiv = document.createElement('div');
            loadingDiv.id = 'map-loading';
            loadingDiv.style.cssText = `
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: rgba(0,0,0,0.8);
                color: white;
                padding: 20px;
                border-radius: 5px;
                z-index: 1000;
            `;
            this.container.appendChild(loadingDiv);
        }
        loadingDiv.textContent = message;
        loadingDiv.style.display = 'block';
    }

    hideLoadingMessage() {
        const loadingDiv = document.getElementById('map-loading');
        if (loadingDiv) {
            loadingDiv.style.display = 'none';
        }
    }
    
    showMessage(message, type = 'info') {
        const messageDiv = document.createElement('div');
        messageDiv.style.cssText = `
            position: absolute;
            top: 20px;
            right: 20px;
            padding: 10px 20px;
            border-radius: 5px;
            color: white;
            z-index: 1000;
            background: ${type === 'error' ? '#dc3545' : type === 'warning' ? '#ffc107' : '#007bff'};
        `;
        messageDiv.textContent = message;
        this.container.appendChild(messageDiv);

        // 3秒后自动删除
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.parentNode.removeChild(messageDiv);
            }
        }, 3000);
    }
    
    // OBJ导出功能
    async exportToOBJ() {
        if (!this.mapData) {
            this.showMessage('No map data loaded', 'error');
            return;
        }

        try {
            this.showLoadingMessage('Generating OBJ model...');

            const response = await fetch(`/api/maps/${this.mapData.id}/export/obj`);
            const result = await response.json();

            this.hideLoadingMessage();

            if (result.success) {
                // 创建下载链接
                const link = document.createElement('a');
                link.href = result.data.download_url;
                link.download = result.data.filename;
                link.click();

                this.showMessage(`OBJ model exported: ${result.data.filename}`, 'success');
            } else {
                this.showMessage('Failed to export OBJ model', 'error');
            }

        } catch (error) {
            this.hideLoadingMessage();
            console.error('Error exporting OBJ:', error);
            this.showMessage('Export failed', 'error');
        }
    }
    
    // 导出指定区域为OBJ
    async exportRegionToOBJ(minCoords, maxCoords) {
        if (!this.mapData) {
            this.showMessage('No map data loaded', 'error');
            return;
        }

        try {
            this.showLoadingMessage('Generating region OBJ model...');

            const params = new URLSearchParams({
                min_x: minCoords.x,
                min_y: minCoords.y,
                min_z: minCoords.z,
                max_x: maxCoords.x,
                max_y: maxCoords.y,
                max_z: maxCoords.z
            });

            const response = await fetch(`/api/maps/${this.mapData.id}/export/obj/region?${params}`);
            const result = await response.json();

            this.hideLoadingMessage();

            if (result.success) {
                const link = document.createElement('a');
                link.href = result.data.download_url;
                link.download = result.data.filename;
                link.click();

                this.showMessage(`Region OBJ model exported: ${result.data.filename}`, 'success');
            } else {
                this.showMessage('Failed to export region OBJ model', 'error');
            }

        } catch (error) {
            this.hideLoadingMessage();
            console.error('Error exporting region OBJ:', error);
            this.showMessage('Export failed', 'error');
        }
    }
}

// 辅助函数
window.MapViewer = MapViewer;