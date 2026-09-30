import { expect, test } from "@playwright/test";

test.describe("Home Assistant test target", () => {
  test("opens the local onboarding or application surface", async ({ page }) => {
    await page.goto("/");

    await expect(page).toHaveURL(/127\.0\.0\.1:8123\/(onboarding\.html)?/);
    await expect(page.locator("body")).toContainText(
      /Home Assistant|Create your account|Sign in|Welcome home|Log in/i,
    );
  });
});
