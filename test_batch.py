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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
