/**
 * CraftNE 主应用程序
 * 全局JavaScript功能和工具函数
 */

// 全局应用对象
window.CraftNE = {
    config: {
        apiBaseUrl: '/api',
        uploadMaxSize: 500 * 1024 * 1024, // 500MB
        supportedFormats: ['mca', 'mcr']
    },

    // 工具函数
    utils: {
        // 格式化文件大小
        formatFileSize: function(bytes) {
            if (bytes === 0) return '0 B';
            const k = 1024;
            const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        },

        // 格式化日期
        formatDate: function(dateString) {
            const date = new Date(dateString);
            return date.toLocaleDateString('zh-CN', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        },

        // 显示通知
        showNotification: function(message, type = 'info', duration = 5000) {
            const alertClass = {
                'success': 'alert-success',
                'error': 'alert-danger',
                'warning': 'alert-warning',
                'info': 'alert-info'
            }[type] || 'alert-info';

            const alertHtml = `
                <div class="alert ${alertClass} alert-dismissible fade show notification-alert" role="alert">
                    <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : type === 'warning' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
                    ${message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `;

            // 添加到页面顶部
            const container = $('.container, .container-fluid').first();
            if (container.length) {
                container.prepend(alertHtml);

                // 自动隐藏
                if (duration > 0) {
                    setTimeout(() => {
                        $('.notification-alert').first().fadeOut(() => {
                            $('.notification-alert').first().remove();
                        });
                    }, duration);
                }
            }
        },

        // 确认对话框
        confirm: function(message, callback) {
            if (window.confirm(message)) {
                callback();
            }
        },

        // 复制到剪贴板
        copyToClipboard: function(text) {
            navigator.clipboard.writeText(text).then(() => {
                this.showNotification('已复制到剪贴板', 'success', 2000);
            }).catch(() => {
                this.showNotification('复制失败', 'error', 2000);
            });
        },

        // 生成随机颜色
        randomColor: function() {
            const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3', '#54A0FF'];
            return colors[Math.floor(Math.random() * colors.length)];
        },

        // 防抖函数
        debounce: function(func, wait, immediate) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    timeout = null;
                    if (!immediate) func(...args);
                };
                const callNow = immediate && !timeout;
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
                if (callNow) func(...args);
            };
        },

        // 节流函数
        throttle: function(func, limit) {
            let inThrottle;
            return function(...args) {
                if (!inThrottle) {
                    func.apply(this, args);
                    inThrottle = true;
                    setTimeout(() => inThrottle = false, limit);
                }
            };
        }
    },

    // API 请求封装
    api: {
        request: function(method, url, data = null, options = {}) {
            const defaultOptions = {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            };

            if (data && method !== 'GET') {
                defaultOptions.body = JSON.stringify(data);
            }

            const finalOptions = { ...defaultOptions, ...options };

            return fetch(url, finalOptions)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    return response.json();
                })
                .catch(error => {
                    console.error('API请求失败:', error);
                    CraftNE.utils.showNotification(`请求失败: ${error.message}`, 'error');
                    throw error;
                });
        },

        get: function(url) {
            return this.request('GET', url);
        },

        post: function(url, data) {
            return this.request('POST', url, data);
        },

        put: function(url, data) {
            return this.request('PUT', url, data);
        },

        delete: function(url) {
            return this.request('DELETE', url);
        }
    },

    // 文件上传管理
    upload: {
        validateFile: function(file) {
            const errors = [];

            // 检查文件大小
            if (file.size > CraftNE.config.uploadMaxSize) {
                errors.push(`文件大小超过限制 (${CraftNE.utils.formatFileSize(CraftNE.config.uploadMaxSize)})`);
            }

            // 检查文件格式
            const extension = file.name.split('.').pop().toLowerCase();
            if (!CraftNE.config.supportedFormats.includes(extension)) {
                errors.push(`不支持的文件格式，支持: ${CraftNE.config.supportedFormats.join(', ')}`);
            }

            return errors;
        },

        uploadFile: function(file, progressCallback, successCallback, errorCallback) {
            const formData = new FormData();
            formData.append('file', file);

            const xhr = new XMLHttpRequest();

            // 进度监听
            if (progressCallback) {
                xhr.upload.addEventListener('progress', (e) => {
                    if (e.lengthComputable) {
                        const progress = (e.loaded / e.total) * 100;
                        progressCallback(progress);
                    }
                });
            }

            // 成功回调
            xhr.addEventListener('load', () => {
                if (xhr.status === 200 || xhr.status === 201) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        if (successCallback) successCallback(response);
                    } catch (e) {
                        if (errorCallback) errorCallback('响应解析失败');
                    }
                } else {
                    try {
                        const error = JSON.parse(xhr.responseText);
                        if (errorCallback) errorCallback(error.error || '上传失败');
                    } catch (e) {
                        if (errorCallback) errorCallback('上传失败');
                    }
                }
            });

            // 错误回调
            xhr.addEventListener('error', () => {
                if (errorCallback) errorCallback('网络错误');
            });

            // 发送请求
            xhr.open('POST', '/upload/api/upload');
            xhr.send(formData);

            return xhr;
        }
    },

    // 本地存储管理
    storage: {
        set: function(key, value) {
            try {
                localStorage.setItem(`craftne_${key}`, JSON.stringify(value));
                return true;
            } catch (e) {
                console.warn('localStorage设置失败:', e);
                return false;
            }
        },

        get: function(key, defaultValue = null) {
            try {
                const item = localStorage.getItem(`craftne_${key}`);
                return item ? JSON.parse(item) : defaultValue;
            } catch (e) {
                console.warn('localStorage获取失败:', e);
                return defaultValue;
            }
        },

        remove: function(key) {
            try {
                localStorage.removeItem(`craftne_${key}`);
                return true;
            } catch (e) {
                console.warn('localStorage删除失败:', e);
                return false;
            }
        },

        clear: function() {
            try {
                Object.keys(localStorage).forEach(key => {
                    if (key.startsWith('craftne_')) {
                        localStorage.removeItem(key);
                    }
                });
                return true;
            } catch (e) {
                console.warn('localStorage清空失败:', e);
                return false;
            }
        }
    }
};

// DOM就绪后初始化
$(document).ready(function() {
    // 初始化工具提示
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // 初始化弹出框
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // 自动隐藏警告框
    setTimeout(() => {
        $('.alert:not(.notification-alert)').fadeOut();
    }, 5000);

    // 全局AJAX设置
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            // 添加CSRF令牌（如果有的话）
            const token = $('meta[name=csrf-token]').attr('content');
            if (token) {
                xhr.setRequestHeader('X-CSRFToken', token);
            }
        },
        error: function(xhr, status, error) {
            if (xhr.status === 401) {
                CraftNE.utils.showNotification('登录已过期，请重新登录', 'warning');
                setTimeout(() => {
                    window.location.href = '/login';
                }, 2000);
            } else if (xhr.status === 403) {
                CraftNE.utils.showNotification('没有权限执行此操作', 'error');
            } else if (xhr.status >= 500) {
                CraftNE.utils.showNotification('服务器错误，请稍后重试', 'error');
            }
        }
    });

    // 键盘快捷键
    $(document).keydown(function(e) {
        // Ctrl+S 保存（阻止浏览器默认行为）
        if (e.ctrlKey && e.which === 83) {
            e.preventDefault();
            // 触发自定义保存事件
            $(document).trigger('craftne:save');
        }

        // ESC 关闭模态框
        if (e.which === 27) {
            $('.modal.show').modal('hide');
        }
    });

    // 全局拖拽文件支持
    let dragCounter = 0;

    $(document).on('dragenter', function(e) {
        e.preventDefault();
        dragCounter++;
        $('body').addClass('drag-over');
    });

    $(document).on('dragleave', function(e) {
        e.preventDefault();
        dragCounter--;
        if (dragCounter <= 0) {
            $('body').removeClass('drag-over');
        }
    });

    $(document).on('dragover', function(e) {
        e.preventDefault();
    });

    $(document).on('drop', function(e) {
        e.preventDefault();
        dragCounter = 0;
        $('body').removeClass('drag-over');

        // 如果在上传页面，处理文件拖拽
        if (window.location.pathname.includes('/upload')) {
            const files = e.originalEvent.dataTransfer.files;
            if (files.length > 0 && $('#fileInput').length) {
                $('#fileInput')[0].files = files;
                $('#fileInput').trigger('change');
            }
        }
    });

    // 响应式表格
    $('.table-responsive').each(function() {
        const $table = $(this).find('table');
        if ($table.length) {
            $table.addClass('table-sm');
        }
    });

    // 自动刷新功能
    if ($('[data-auto-refresh]').length) {
        const interval = parseInt($('[data-auto-refresh]').attr('data-auto-refresh')) || 30000;
        setInterval(() => {
            $('[data-auto-refresh]').each(function() {
                const $element = $(this);
                const url = $element.data('refresh-url');
                if (url) {
                    $.get(url).done((data) => {
                        $element.html(data);
                    });
                }
            });
        }, interval);
    }

    console.log('CraftNE应用初始化完成');
});

// 页面卸载前保存状态
$(window).on('beforeunload', function() {
    // 保存当前页面状态到本地存储
    const currentPage = window.location.pathname;
    CraftNE.storage.set('lastVisitedPage', currentPage);

    // 保存表单数据（如果有未保存的）
    $('form[data-autosave]').each(function() {
        const formId = $(this).attr('id');
        if (formId) {
            const formData = $(this).serialize();
            CraftNE.storage.set(`form_${formId}`, formData);
        }
    });
});

// 导出到全局作用域
window.CraftNE = CraftNE;
