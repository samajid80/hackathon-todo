/**
 * Confirm Dialog Component (T128)
 *
 * Features:
 * - Modal dialog overlay
 * - Customizable message/question text
 * - Confirm and Cancel buttons
 * - Red styling for destructive actions
 * - Click outside to close
 * - Keyboard support (Escape to cancel, Enter to confirm)
 * - Accessibility: ARIA roles, focus management
 * - Smooth transitions
 */

"use client";

import React, { useEffect, useRef } from "react";
import { Button } from "./ui/Button";

export interface ConfirmDialogProps {
  isOpen: boolean;
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  onConfirm: () => void;
  onCancel: () => void;
  variant?: "danger" | "primary";
}

export const ConfirmDialog: React.FC<ConfirmDialogProps> = ({
  isOpen,
  title,
  message,
  confirmLabel = "Confirm",
  cancelLabel = "Cancel",
  onConfirm,
  onCancel,
  variant = "danger",
}) => {
  const dialogRef = useRef<HTMLDivElement>(null);
  const confirmButtonRef = useRef<HTMLButtonElement>(null);

  // Handle keyboard events
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onCancel();
      } else if (event.key === "Enter") {
        onConfirm();
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onConfirm, onCancel]);

  // Focus management: focus the confirm button when dialog opens
  useEffect(() => {
    if (isOpen && confirmButtonRef.current) {
      confirmButtonRef.current.focus();
    }
  }, [isOpen]);

  // Prevent body scroll when dialog is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "unset";
    }

    return () => {
      document.body.style.overflow = "unset";
    };
  }, [isOpen]);

  // Handle click outside
  const handleOverlayClick = (event: React.MouseEvent<HTMLDivElement>) => {
    if (event.target === event.currentTarget) {
      onCancel();
    }
  };

  if (!isOpen) {
    return null;
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 transition-opacity duration-200"
      onClick={handleOverlayClick}
      role="dialog"
      aria-modal="true"
      aria-labelledby="dialog-title"
      aria-describedby="dialog-description"
    >
      <div
        ref={dialogRef}
        className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 transform transition-all duration-200 scale-100 opacity-100"
        role="document"
      >
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200">
          <h2
            id="dialog-title"
            className="text-xl font-semibold text-gray-900"
          >
            {title}
          </h2>
        </div>

        {/* Body */}
        <div className="px-6 py-4">
          <p
            id="dialog-description"
            className="text-gray-700"
          >
            {message}
          </p>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-gray-50 rounded-b-lg flex justify-end gap-3">
          <Button
            variant="secondary"
            onClick={onCancel}
            className="px-4 py-2"
            aria-label="Cancel action"
          >
            {cancelLabel}
          </Button>
          <Button
            ref={confirmButtonRef}
            variant={variant}
            onClick={onConfirm}
            className="px-4 py-2"
            aria-label="Confirm action"
          >
            {confirmLabel}
          </Button>
        </div>
      </div>
    </div>
  );
};
