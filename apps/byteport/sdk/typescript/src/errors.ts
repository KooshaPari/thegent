/**
 * BytePort error classes
 */

export class BytePortError extends Error {
  constructor(
    message: string,
    public statusCode: number = 0,
    public details: string = ''
  ) {
    super(
      details
        ? `BytePort API error (status ${statusCode}): ${message} - ${details}`
        : `BytePort API error (status ${statusCode}): ${message}`
    )
    this.name = 'BytePortError'
  }
}

export class NotFoundError extends BytePortError {
  constructor(message: string, details: string = '') {
    super(message, 404, details)
    this.name = 'NotFoundError'
  }
}

export class BadRequestError extends BytePortError {
  constructor(message: string, details: string = '') {
    super(message, 400, details)
    this.name = 'BadRequestError'
  }
}

export class ServerError extends BytePortError {
  constructor(message: string, details: string = '') {
    super(message, 500, details)
    this.name = 'ServerError'
  }
}
