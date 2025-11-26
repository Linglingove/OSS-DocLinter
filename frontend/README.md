# OSS-DocLinter Frontend

This is the frontend application for the OSS-DocLinter tool, built with React, TypeScript, and Ant Design.

## Features

- **Repository Analysis**: Input a GitHub URL to scan documentation.
- **Quality Dashboard**: View overall scores, completeness checks, and formatting issues.
- **Detailed Reports**: Drill down into specific issues with suggestions.
- **Auto-Fix & Preview**: Generate AI-powered fixes and preview changes with a diff viewer.
- **One-Click PR**: Submit fixes directly to GitHub (requires authentication).

## Tech Stack

- **Framework**: React 18 + Vite
- **Language**: TypeScript
- **UI Library**: Ant Design
- **HTTP Client**: Axios
- **Routing**: React Router DOM
- **Diff Viewer**: react-diff-viewer-continued

## Getting Started

1.  **Install Dependencies**

    ```bash
    npm install
    # or
    yarn install
    ```

2.  **Run Development Server**

    ```bash
    npm run dev
    # or
    yarn dev
    ```

3.  **Build for Production**

    ```bash
    npm run build
    ```

## Configuration

The API base URL is configured in `vite.config.ts` to proxy requests to `http://localhost:5147`. Adjust this if your backend runs on a different port.
