class DomainError extends Error {
  constructor(message, code = "DOMAIN_ERROR", status = 400) {
    super(message);
    this.code = code;
    this.status = status;
  }

  static notFound(message = "RESOURCE NOT FOUND") {
    return new DomainError(message, "NOT_FOUND", 404);
  }

  static invalid(message = "INVALID INPUT") {
    return new DomainError(message, "INVALID_INPUT", 400);
  }
}

export { DomainError };