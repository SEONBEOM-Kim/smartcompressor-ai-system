/**
 * Template Renderer for Notification Dashboard
 * Renders notification templates in the UI
 */

import { getTypeColor } from '../utils/formatters.js';
import { showToast } from '../utils/toast-manager.js';

class TemplateRenderer {
    constructor(dataLoader) {
        this.dataLoader = dataLoader;
    }

    /**
     * Render the templates tab content
     */
    async renderTemplates() {
        try {
            const templates = await this.dataLoader.loadTemplates();
            this.displayTemplates(templates);
        } catch (error) {
            console.error('Error rendering templates:', error);
            showToast('템플릿 데이터 로드 중 오류가 발생했습니다.', 'error');
        }
    }

    /**
     * Display templates in the UI
     */
    displayTemplates(templates) {
        const tbody = document.getElementById('templateList');
        if (!tbody) return;

        // Clear existing content
        tbody.innerHTML = '';

        if (templates) {
            templates.forEach(template => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${template.template_id || ''}</td>
                    <td>${template.name || ''}</td>
                    <td><span class="badge badge-info">${template.category || ''}</span></td>
                    <td>${template.variables ? template.variables.join(', ') : ''}</td>
                    <td><span class="badge badge-${template.is_active ? 'success' : 'secondary'}">${template.is_active ? '활성' : '비활성'}</span></td>
                    <td>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-primary" onclick="dashboard && dashboard.editTemplate ? dashboard.editTemplate('${template.template_id}') : editTemplate('${template.template_id}')">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-outline-danger" onclick="dashboard && dashboard.deleteTemplate ? dashboard.deleteTemplate('${template.template_id}') : deleteTemplate('${template.template_id}')">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </td>
                `;
                tbody.appendChild(row);
            });
        }
    }
}

// Export the class for use in other modules
export default TemplateRenderer;