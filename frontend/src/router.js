import { userResource } from "@/data/user"
import { createRouter, createWebHistory } from "vue-router"
import { session } from "./data/session"

const routes = [
	{
		path: "/",
		name: "Home",
		redirect: "/dashboard"
	},
	{
		path: "/dashboard",
		name: "Dashboard",
		component: () => import("@/pages/Dashboard.vue"),
	},
	{
		path: "/bookings",
		name: "Bookings",
		component: () => import("@/pages/Bookings.vue"),
	},
	{
		path: "/clients",
		name: "Clients",
		component: () => import("@/pages/Clients.vue"),
	},
	{
		path: "/photographers",
		name: "Photographers",
		component: () => import("@/pages/Photographers.vue"),
	},
	{
		path: "/studios",
		name: "Studios",
		component: () => import("@/pages/Studios.vue"),
	},
	{
		path: "/packages",
		name: "Packages",
		component: () => import("@/pages/Packages.vue"),
	},

	{
		name: "Login",
		path: "/account/login",
		component: () => import("@/pages/Login.vue"),
	},
]

const router = createRouter({
	history: createWebHistory("/frontend"),
	routes,
})

router.beforeEach(async (to, from, next) => {
	let isLoggedIn = session.isLoggedIn
	try {
		await userResource.promise
	} catch (error) {
		isLoggedIn = false
	}

	if (to.name === "Login" && isLoggedIn) {
		next({ name: "Home" })
	} else if (to.name !== "Login" && !isLoggedIn) {
		next({ name: "Login" })
	} else {
		next()
	}
})

export default router
