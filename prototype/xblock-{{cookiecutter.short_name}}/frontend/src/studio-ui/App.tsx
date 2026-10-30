import { useHandlerUrl, RuntimeContext, saveStudioBlock } from "@opencraft/xblock-react-utils";
import { useContext } from "react";
import { Formik } from "formik";
import { Editor } from "./components/Editor.tsx";
import type { {{cookiecutter.class_name}}Fields } from "@/types.ts";

export const App = (data: {{cookiecutter.class_name}}Fields) => {
  const { runtime } = useContext(RuntimeContext);
  const studioSaveUrl = useHandlerUrl("studio_save");
  const handleSave = (saveData: {{cookiecutter.class_name}}Fields) => {
    // Convenience function that wraps calls to the server with runtime notifications
    // so users see the 'saving' indicator.
    void saveStudioBlock<{{cookiecutter.class_name}}Fields>({
      saveUrl: studioSaveUrl,
      data: saveData,
      runtime,
    });
  };
  return (
    <Formik initialValues={data} onSubmit={handleSave}>
      <Editor />
    </Formik>
  );
};
