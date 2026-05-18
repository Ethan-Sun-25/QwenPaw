import { Empty } from "antd";
import { useTranslation } from "react-i18next";

export default function McpTab() {
  const { t } = useTranslation();
  return (
    <div style={{ padding: "48px 0" }}>
      <Empty description={t("dashboard.empty.placeholder")} />
    </div>
  );
}
