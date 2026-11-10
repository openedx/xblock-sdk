import { describe, it, beforeEach, afterEach } from "vitest";
import userEvent from "@testing-library/user-event";
import { waitFor } from "@testing-library/react";
import { initDataFactory, specRender } from "@/lib/specHelpers.tsx";
import { App } from "./App.tsx";

describe("App.tsx", () => {
  beforeEach(() => {
    $.mockjax({
      url: "/handler/increment",
      method: "POST",
      data: JSON.stringify({ code: "Bork" }),
      contentType: "application/json",
      responseText: { count: 10 },
    });
  });
  afterEach(() => {
    $.mockjax.clearAll();
  });
  it("renders", () => {
    const { screen } = specRender(<App {...initDataFactory()} />);
    // getByText throws if the query fails. Check the React Testing
    // Library documentation for more details.
    screen.getByText("Count: 0");
    screen.getByRole("button", { name: "Increase" });
  });
  it("increments", async () => {
    const user = userEvent.setup();
    const { screen } = specRender(<App {...initDataFactory({ code: "Bork", count: 1 })} />);
    // getByText throws if the query fails. Check the React Testing
    // Library documentation for more details.
    const button = screen.getByRole("button", { name: "Increase" });
    await user.click(button);
    await waitFor(() => screen.getByText("Count: 10"));
  });
});
