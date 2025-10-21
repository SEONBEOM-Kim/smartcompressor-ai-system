/**
 * Template Creator for Notification Dashboard
 * Handles template creation form processing
 */

import { showToast } from '../utils/toast-manager.js';

class TemplateCreator {
    constructor(dataLoader) {
        this.dataLoader = dataLoader;
        this.init();
    }

    init() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Add event listener to the template form
        const form = document.getElementById('templateForm');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.createTemplate();
            });
        }
    }

    /**
     * Create a new template from form data
     */
    async createTemplate() {
        try {
            const templateData = {
                template_id: document.getElementById('templateId').value,
                name: document.getElementById('templateName').value,
                subject: document.getElementById('templateSubject').value,
                html_content: document.getElementById('templateHtml').value,
                text_content: document.getElementById('templateText').value,
                variables: document.getElementById('templateVariables').value.split(',').map(v => v.trim()),
                category: document.getElementById('templateCategory').value
            };

            const response = await this.dataLoader.createTemplate(templateData);

            if (response.success) {
                showToast('템플릿이 생성되었습니다.', 'success');
                
                // Close the modal if it exists
                const templateModal = document.getElementById('templateModal');
                if (templateModal && bootstrap) {
                    const modal = bootstrap.Modal.getInstance(templateModal);
                    if (modal) {
                        modal.hide();
                    } else {
                        // Fallback if modal instance isn't available
                        templateModal.querySelector('.btn-close')?.click();
                    }
                }
                
                // Reset form
                document.getElementById('templateForm').reset();
                
                // Trigger template list refresh if dashboard is available
                if (window.dashboard && typeof window.dashboard.loadTemplates === 'function') {
                    window.dashboard.loadTemplates();
                }
            } else {
                showToast('템플릿 생성에 실패했습니다.', 'error');
            }
        } catch (error) {
            console.error('Error creating template:', error);
            showToast('템플릿 생성 중 오류가 발생했습니다.', 'error');
        }
    }
}

// Export the class for use in other modules
export default TemplateCreator;