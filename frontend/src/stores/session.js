import { createResource } from 'frappe-ui'
import { reactive } from 'vue'

export const sessionStore = reactive({
  isLoggedIn: false,
  user: null,
  
  async login(email, password) {
    const loginResource = createResource({
      url: 'login',
      params: {
        usr: email,
        pwd: password,
      },
      onSuccess() {
        this.isLoggedIn = true
        this.user = loginResource.data
      },
    })
    
    return await loginResource.submit()
  },
  
  async logout() {
    const logoutResource = createResource({
      url: 'logout',
      onSuccess() {
        this.isLoggedIn = false
        this.user = null
      },
    })
    
    return await logoutResource.submit()
  },
  
  async checkSession() {
    const sessionResource = createResource({
      url: 'frappe.auth.get_logged_user',
      onSuccess(data) {
        if (data) {
          this.isLoggedIn = true
          this.user = data
        } else {
          this.isLoggedIn = false
          this.user = null
        }
      },
    })
    
    return await sessionResource.submit()
  }
})