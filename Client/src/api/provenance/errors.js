export class ApiError extends Error {
  constructor(message, { status = null, detail = null, code = null, payload = null } = {}) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
    this.code = code;
    this.payload = payload;
  }
}

export function getErrorMessage(error) {
  if (error instanceof ApiError) {
    if (typeof error.detail === "string") return error.detail;
    if (Array.isArray(error.detail)) return error.detail.map((item) => item.msg || JSON.stringify(item)).join("; ");
    return error.message;
  }
  return error?.message || "Something went wrong. Please try again.";
}
