// Re Studio Booking Sidebar JavaScript

// Check if ReStudioSidebar is already defined
if (typeof window.ReStudioSidebar === 'undefined') {
    window.ReStudioSidebar = class {
        constructor() {
            this.isOpen = false;
            this.sidebar = null;
            this.toggleBtn = null;
            this.overlay = null;
            this.closeBtn = null;
        }

        init() {
            this.createSidebar();
            this.bindEvents();
            this.updateActiveMenuItem();
        }

        createSidebar() {
            // Create sidebar HTML
            const sidebarHTML = `
                <!-- Sidebar Toggle Button -->
                <button class="sidebar-toggle" id="sidebarToggle">
                    <span></span>
                    <span></span>
                    <span></span>
                </button>
                
                <!-- Sidebar -->
                <div class="re-studio-sidebar collapsed" id="reStudioSidebar">
                    <div class="sidebar-header">
                        <h3 class="sidebar-title">Re Studio 📸</h3>
                        <button class="sidebar-close" id="sidebarClose">&times;</button>
                    </div>
                    
                    <nav class="sidebar-menu">
                        <a href="/re_studio_booking/dashboard" class="menu-item" data-page="dashboard">
                            <i class="icon">🏠</i>
                            <span>لوحة التحكم</span>
                        </a>
                        
                        <a href="/re_studio_booking/services" class="menu-item" data-page="services">
                            <i class="icon">🛠️</i>
                            <span>إدارة الخدمات</span>
                        </a>
                        
                        <a href="/re_studio_booking/photographers" class="menu-item" data-page="photographers">
                            <i class="icon">👥</i>
                            <span>إدارة المصورين</span>
                        </a>
                        
                        <a href="/re_studio_booking/bookings" class="menu-item" data-page="bookings">
                            <i class="icon">📅</i>
                            <span>إدارة الحجوزات</span>
                        </a>
                        
                        <a href="/re_studio_booking/calendar" class="menu-item" data-page="calendar">
                            <i class="icon">🗓️</i>
                            <span>عرض التقويم</span>
                        </a>
                        
                        <a href="/re_studio_booking/users" class="menu-item" data-page="users">
                            <i class="icon">👤</i>
                            <span>إدارة المستخدمين والأدوار</span>
                        </a>
                        
                        <a href="/re_studio_booking/files" class="menu-item" data-page="files">
                            <i class="icon">📁</i>
                            <span>ملفات الحجوزات</span>
                        </a>
                        
                        <a href="/re_studio_booking/reports" class="menu-item" data-page="reports">
                            <i class="icon">📈</i>
                            <span>التقارير</span>
                        </a>
                        
                        <a href="/re_studio_booking/settings" class="menu-item" data-page="settings">
                            <i class="icon">⚙️</i>
                            <span>الإعدادات</span>
                        </a>
                    </nav>
                </div>
                
                <!-- Sidebar Overlay -->
                <div class="sidebar-overlay" id="sidebarOverlay"></div>
            `;
            
            // Insert sidebar HTML into body
            document.body.insertAdjacentHTML('beforeend', sidebarHTML);
            
            // Get references
            this.sidebar = document.getElementById('reStudioSidebar');
            this.toggleBtn = document.getElementById('sidebarToggle');
            this.overlay = document.getElementById('sidebarOverlay');
            this.closeBtn = document.getElementById('sidebarClose');
        }

        bindEvents() {
            if (this.toggleBtn) {
                this.toggleBtn.addEventListener('click', () => this.toggleSidebar());
            }
            
            if (this.closeBtn) {
                this.closeBtn.addEventListener('click', () => this.closeSidebar());
            }
            
            if (this.overlay) {
                this.overlay.addEventListener('click', () => this.closeSidebar());
            }
            
            // Close sidebar on escape key
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && this.isOpen) {
                    this.closeSidebar();
                }
            });
        }

        toggleSidebar() {
            if (this.isOpen) {
                this.closeSidebar();
            } else {
                this.openSidebar();
            }
        }

        openSidebar() {
            if (this.sidebar) {
                this.sidebar.classList.remove('collapsed');
                this.overlay.classList.add('active');
                this.isOpen = true;
                document.body.style.overflow = 'hidden';
            }
        }

        closeSidebar() {
            if (this.sidebar) {
                this.sidebar.classList.add('collapsed');
                this.overlay.classList.remove('active');
                this.isOpen = false;
                document.body.style.overflow = '';
            }
        }

        updateActiveMenuItem() {
            const currentPath = window.location.pathname;
            const menuItems = document.querySelectorAll('.menu-item');
            
            menuItems.forEach(item => {
                item.classList.remove('active');
                if (item.getAttribute('href') === currentPath) {
                    item.classList.add('active');
                }
            });
        }
    };
}

// Initialize sidebar when DOM is loaded
(function() {
    function initSidebar() {
        // Check if sidebar already exists
        if (document.getElementById('reStudioSidebar')) {
            return;
        }
        
        const sidebar = new window.ReStudioSidebar();
        sidebar.init();
    }
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSidebar);
    } else {
        initSidebar();
    }
})();