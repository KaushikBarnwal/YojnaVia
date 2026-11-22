import { ref } from 'vue';

export interface Toast {
  id: string;
  message: string;
  type: 'success' | 'error' | 'info';
  duration?: number;
}

export const toasts = ref<Toast[]>([]);

export function showToast(message: string, type: 'success' | 'error' | 'info' = 'success', duration = 3500) {
  const id = 'toast_' + Math.random().toString(36).substring(2, 9);
  const toast: Toast = { id, message, type, duration };
  toasts.value.push(toast);

  setTimeout(() => {
    removeToast(id);
  }, duration);
}

export function removeToast(id: string) {
  toasts.value = toasts.value.filter(t => t.id !== id);
}
