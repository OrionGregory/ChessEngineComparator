import React from "react";
import { createRoot } from "react-dom/client"; // Import createRoot
import { BrowserRouter } from "react-router-dom"; // Import BrowserRouter
import Auth from "./Auth";

const container = document.getElementById("root");
const root = createRoot(container); // Create a root for React 18

root.render(
  <BrowserRouter>
    <Auth />
  </BrowserRouter>
);