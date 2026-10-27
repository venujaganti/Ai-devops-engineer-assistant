from src.devops_ai.ui import (
    chat,
    cloud_inventory,
    code_lab,
    knowledge,
    navigation,
    pipelines,
    security,
    settings_page,
    theme,
)


def test_all_navigation_targets_are_unique():
    targets = list(navigation.PAGES.values())

    assert len(targets) == len(set(targets))


def test_all_navigation_targets_have_page_renderers():
    renderers = {
        "chat",
        "knowledge",
        "code_lab",
        "cloud_inventory",
        "pipelines",
        "security",
        "settings",
    }

    targets = set(navigation.PAGES.values())
    targets.discard("overview")

    assert targets == renderers


def test_code_lab_has_supported_examples():
    assert "Terraform" in code_lab.EXAMPLES
    assert "Kubernetes" in code_lab.EXAMPLES
    assert "Jenkins" in code_lab.EXAMPLES
    assert "Azure Pipelines" in code_lab.EXAMPLES
    assert "Google Cloud Build" in code_lab.EXAMPLES


def test_documentation_sources_are_https():
    assert knowledge.SOURCES

    for url in knowledge.SOURCES.values():
        assert url.startswith("https://")


def test_cloud_inventory_has_three_providers():
    providers = {
        entry["provider"]
        for entry in cloud_inventory.PROVIDERS
    }

    assert providers == {
        "AWS",
        "Microsoft Azure",
        "Google Cloud",
    }


def test_pipeline_catalog_contains_required_platforms():
    platforms = {
        entry["platform"]
        for entry in pipelines.PIPELINES
    }

    assert "Jenkins" in platforms
    assert "Azure Pipelines" in platforms
    assert "Google Cloud Build" in platforms


def test_security_catalog_contains_required_tools():
    names = {name for name, _ in security.TOOLS}

    assert "Trivy" in names
    assert "SonarQube" in names
    assert "Gitleaks" in names


def test_all_page_modules_expose_render_functions():
    assert callable(chat.render_chat)
    assert callable(knowledge.render_knowledge)
    assert callable(code_lab.render_code_lab)
    assert callable(cloud_inventory.render_cloud_inventory)
    assert callable(pipelines.render_pipelines)
    assert callable(security.render_security)
    assert callable(settings_page.render_settings)
    assert callable(theme.apply_theme)