#!/usr/bin/env python3
"""
Playwright tests for Batch Conversion feature.
Tests the UI workflow for both single file and batch conversion modes.
"""
import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:8085"


def test_page_loads(page: Page):
    """Test that the main page loads correctly."""
    page.goto(BASE_URL)
    expect(page).to_have_title("Bambu to Snapmaker U1 Converter")
    # Check header is visible
    expect(page.locator("h1")).to_contain_text("Bambu")
    expect(page.locator("h1")).to_contain_text("Snapmaker U1")


def test_mode_toggle_exists(page: Page):
    """Test that single/batch mode toggle buttons exist."""
    page.goto(BASE_URL)
    single_btn = page.locator("#single-mode-btn")
    batch_btn = page.locator("#batch-mode-btn")

    expect(single_btn).to_be_visible()
    expect(batch_btn).to_be_visible()
    expect(single_btn).to_contain_text("Single File")
    expect(batch_btn).to_contain_text("Batch Convert")


def test_single_mode_is_default(page: Page):
    """Test that single file mode is the default."""
    page.goto(BASE_URL)
    single_mode = page.locator("#single-mode")
    batch_mode = page.locator("#batch-mode")

    # Single mode should be visible, batch mode hidden
    expect(single_mode).to_be_visible()
    expect(batch_mode).to_be_hidden()


def test_switch_to_batch_mode(page: Page):
    """Test switching to batch mode."""
    page.goto(BASE_URL)

    # Click batch mode button
    page.locator("#batch-mode-btn").click()

    single_mode = page.locator("#single-mode")
    batch_mode = page.locator("#batch-mode")

    # Now batch mode should be visible
    expect(batch_mode).to_be_visible()
    expect(single_mode).to_be_hidden()


def test_batch_drop_zone_exists(page: Page):
    """Test that batch drop zone exists in batch mode."""
    page.goto(BASE_URL)
    page.locator("#batch-mode-btn").click()

    drop_zone = page.locator("#batch-drop-zone")
    expect(drop_zone).to_be_visible()
    expect(drop_zone).to_contain_text("Click to select a folder")


def test_switch_back_to_single_mode(page: Page):
    """Test switching back from batch to single mode."""
    page.goto(BASE_URL)

    # Switch to batch
    page.locator("#batch-mode-btn").click()
    expect(page.locator("#batch-mode")).to_be_visible()

    # Switch back to single
    page.locator("#single-mode-btn").click()
    expect(page.locator("#single-mode")).to_be_visible()
    expect(page.locator("#batch-mode")).to_be_hidden()


def test_info_modal_opens(page: Page):
    """Test that the info modal opens when clicking the info button."""
    page.goto(BASE_URL)

    # Info modal should be hidden initially
    modal = page.locator("#info-modal")
    expect(modal).to_be_hidden()

    # Click info button
    page.locator("#info-btn").click()
    expect(modal).to_be_visible()
    expect(modal).to_contain_text("What does this tool do?")
    expect(modal).to_contain_text("Batch mode")


def test_info_modal_closes(page: Page):
    """Test that the info modal closes."""
    page.goto(BASE_URL)

    page.locator("#info-btn").click()
    expect(page.locator("#info-modal")).to_be_visible()

    # Close by clicking X
    page.locator("#close-modal").click()
    expect(page.locator("#info-modal")).to_be_hidden()


def test_single_file_drop_zone_exists(page: Page):
    """Test that single file drop zone exists."""
    page.goto(BASE_URL)

    drop_zone = page.locator("#drop-zone")
    expect(drop_zone).to_be_visible()
    expect(drop_zone).to_contain_text("Click to upload")
    expect(drop_zone).to_contain_text("drag and drop")


def test_filament_types_endpoint(page: Page):
    """Test that filament types API returns data."""
    page.goto(BASE_URL)
    response = page.request.get(f"{BASE_URL}/filament-types")
    assert response.ok
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert 'type' in data[0]
    assert 'settings_id' in data[0]


# ========== GUI Enhancement Tests ==========

def test_settings_button_exists(page: Page):
    """Test that settings gear icon exists in header."""
    page.goto(BASE_URL)
    settings_btn = page.locator("#settings-btn")
    expect(settings_btn).to_be_visible()


def test_settings_panel_opens(page: Page):
    """Test that settings panel opens when clicking gear icon."""
    page.goto(BASE_URL)

    # Settings panel should be hidden initially
    panel = page.locator("#settings-panel")
    expect(panel).to_be_hidden()

    # Click settings button
    page.locator("#settings-btn").click()
    expect(panel).to_be_visible()
    expect(panel).to_contain_text("Settings")
    expect(panel).to_contain_text("Output Folder")
    expect(panel).to_contain_text("Source Folder")


def test_settings_panel_closes(page: Page):
    """Test that settings panel closes."""
    page.goto(BASE_URL)

    page.locator("#settings-btn").click()
    expect(page.locator("#settings-panel")).to_be_visible()

    # Close by clicking X
    page.locator("#close-settings").click()
    expect(page.locator("#settings-panel")).to_be_hidden()


def test_settings_api_get(page: Page):
    """Test that settings API returns data."""
    page.goto(BASE_URL)
    response = page.request.get(f"{BASE_URL}/settings")
    assert response.ok
    data = response.json()
    assert 'output_folder' in data
    assert 'source_folder' in data
    assert 'auto_detect' in data
    assert 'delete_duplicates' in data


def test_settings_api_post(page: Page):
    """Test that settings can be updated via API."""
    page.goto(BASE_URL)
    response = page.request.post(f"{BASE_URL}/settings", data={
        "output_folder": "/tmp/test_output",
        "source_folder": "/tmp/test_source",
        "auto_detect": True,
        "delete_duplicates": True
    })
    assert response.ok
    data = response.json()
    assert data.get('success') is True


def test_history_api(page: Page):
    """Test that history API returns data."""
    page.goto(BASE_URL)
    response = page.request.get(f"{BASE_URL}/history")
    assert response.ok
    data = response.json()
    assert isinstance(data, list)


def test_browse_api(page: Page):
    """Test that browse API returns directory listing."""
    page.goto(BASE_URL)
    response = page.request.get(f"{BASE_URL}/browse?path=/")
    assert response.ok
    data = response.json()
    assert 'path' in data
    assert 'dirs' in data


def test_check_new_api(page: Page):
    """Test that check-new API returns data."""
    page.goto(BASE_URL)
    response = page.request.get(f"{BASE_URL}/check-new")
    assert response.ok
    data = response.json()
    assert 'new_files' in data
    assert 'count' in data


def test_folder_browser_modal(page: Page):
    """Test that folder browser modal opens."""
    page.goto(BASE_URL)

    # Open settings panel first
    page.locator("#settings-btn").click()
    expect(page.locator("#settings-panel")).to_be_visible()

    # Folder browser should be hidden initially
    browser = page.locator("#folder-browser")
    expect(browser).to_be_hidden()

    # Click browse output button
    page.locator("#browse-output").click()
    expect(browser).to_be_visible()
    expect(browser).to_contain_text("Select Folder")


def test_new_files_badge_exists(page: Page):
    """Test that new files badge element exists on batch button."""
    page.goto(BASE_URL)
    badge = page.locator("#new-files-badge")
    # Badge exists but may be hidden initially
    expect(badge).to_be_attached()


def test_new_files_alert_exists_in_batch_mode(page: Page):
    """Test that new files alert exists in batch mode."""
    page.goto(BASE_URL)
    page.locator("#batch-mode-btn").click()

    alert = page.locator("#new-files-alert")
    # Alert exists but may be hidden (no new files)
    expect(alert).to_be_attached()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
