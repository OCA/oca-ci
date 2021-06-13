{
    "name": "addon_with_deb_dep2",
    "summary": "Depends on 'curl' debian dependency, and on addon_with_deb_dep.",
    "version": "1.0.0",
    "depends": [
        "addon_with_deb_dep",
    ],
    "external_dependencies": {
        "deb": ["curl"],
    }
}
