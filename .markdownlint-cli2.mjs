export default {
  config: {
    default: true,
    MD013: false,
    MD024: { siblings_only: true },
    MD033: false,
    MD036: false,
    MD041: false,
    MD046: { style: "fenced" },
  },
  globs: ["AGENTS.md", "README.md", "docs/**/*.md", ".github/**/*.md", "SECURITY.md"],
  ignores: ["node_modules/**", ".git/**"],
};
