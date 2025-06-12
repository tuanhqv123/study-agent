import React from "react";

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error("Error caught by boundary:", error, errorInfo);
    this.setState({
      error: error,
      errorInfo: errorInfo,
    });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-6">
          <h1 className="text-xl font-bold text-red-600 mb-4">
            Something went wrong.
          </h1>
          <details className="whitespace-pre-wrap">
            <summary className="cursor-pointer mb-2">Error Details</summary>
            <p className="text-sm text-gray-600 mb-2">
              {this.state.error && this.state.error.toString()}
            </p>
            <p className="text-sm text-gray-500">
              {this.state.errorInfo && this.state.errorInfo.componentStack}
            </p>
          </details>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
