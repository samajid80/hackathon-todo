/**
 * Toast Renderer Component (T140)
 *
 * This component connects the ToastContext to the ToastContainer
 * to render all active toasts in the app.
 */

"use client";

import React from "react";
import { useToast } from "@/lib/toast-context";
import { ToastContainer } from "./Toast";

export function ToastRenderer(): React.ReactElement {
  const { toasts, removeToast } = useToast();

  return <ToastContainer toasts={toasts} onRemove={removeToast} />;
}
