import frappe

# Brings sites installed before the thinkNXG rebrand in line with a fresh install
# (erpnext/setup/install.py). Only standard, untouched values are changed, so
# anything a site administrator customised is left alone.

# "thinkNXG" is what the thinkNXG Framework patch leaves behind; ERP sites get the ERP name,
# as a fresh install does.
OLD_APP_NAMES = {"ERPNext", "Frappe", "thinkNXG", ""}

HELP_ROUTE_MAP = {
	"https://docs.erpnext.com": "https://docs.thinknxg.com/thinknxgerp",
	"https://docs.erpnext.com/": "https://docs.thinknxg.com/thinknxgerp",
	"https://docs.erpnext.com/docs/v14/user/manual/en/introduction": "https://docs.thinknxg.com/thinknxgerp",
	"https://docs.frappe.io/erpnext": "https://docs.thinknxg.com/thinknxgerp",
	"https://docs.frappe.io/erpnext/": "https://docs.thinknxg.com/thinknxgerp",
	"https://docs.thinknxg.com/": "https://docs.thinknxg.com/thinknxgerp",
	"https://discuss.frappe.io": "https://discuss.thinknxg.com",
	"https://discuss.erpnext.com": "https://discuss.thinknxg.com",
	"https://frappe.io/school?utm_source=in_app": "https://thinknxg.school",
	"https://github.com/frappe/erpnext/issues": "https://github.com/thinknxg/thinkNXG-ERP/issues",
	"https://github.com/thinkNXG/thinkNXG-ERP/issues": "https://github.com/thinknxg/thinkNXG-ERP/issues",
}

ERP_DOCS = "https://docs.thinknxg.com/thinknxgerp"
FRAMEWORK_DOCS = "https://docs.thinknxg.com/thinknxgframework"

LABEL_MAP = {"Frappe School": "thinkNXG School"}


def execute():
	app_name = frappe.db.get_single_value("System Settings", "app_name") or ""
	if app_name in OLD_APP_NAMES:
		frappe.db.set_single_value("System Settings", "app_name", "thinkNXG ERP", update_modified=False)

	navbar_settings = frappe.get_single("Navbar Settings")
	changed = False
	for item in navbar_settings.help_dropdown:
		if not item.is_standard:
			continue
		new_route = HELP_ROUTE_MAP.get((item.route or "").strip())
		# "Documentation" is the thinkNXG Framework's own standard item (merged by label with
		# ERPNext's old one), so it goes to the Framework docs; ERP docs get their own entry below.
		if new_route and item.item_label == "Documentation":
			new_route = FRAMEWORK_DOCS
		if new_route:
			item.route = new_route
			changed = True
		if item.item_label in LABEL_MAP:
			item.item_label = LABEL_MAP[item.item_label]
			changed = True

	# The thinkNXG Framework already ships a "Documentation" (framework docs) and a
	# "thinkNXG Support" item, so ERP sites get their own ERP documentation entry.
	routes = {(d.route or "").rstrip("/") for d in navbar_settings.help_dropdown}
	if ERP_DOCS not in routes:
		navbar_settings.append(
			"help_dropdown",
			{
				"item_label": "thinkNXG ERP Documentation",
				"item_type": "Route",
				"route": ERP_DOCS,
				"is_standard": 1,
			},
		)
		changed = True

	if changed:
		navbar_settings.save(ignore_permissions=True)
