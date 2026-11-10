import { ActionRow, Button } from "@openedx/paragon";
import { useContext } from "react";
import { RuntimeContext } from "@opencraft/xblock-react-utils";
import { {{cookiecutter.class_name}}Form } from "./{{cookiecutter.class_name}}Form.tsx";
import { useFormikContext } from "formik";

export const Editor = () => {
  const { runtime } = useContext(RuntimeContext);
  const form = useFormikContext();
  return (
    <div className="react-studio-block">
      <div className="{{cookiecutter.short_name}}-editor editor-with-buttons">
        <div className="wrapper-comp-settings is-active {{cookiecutter.short_name}}-editor-body">
          <{{cookiecutter.class_name}}Form />
        </div>
        <div className="xblock-actions {{cookiecutter.short_name}}-editor-actions">
          <ActionRow>
            <ActionRow.Spacer />
            <Button variant="tertiary" onClick={() => runtime.notify("cancel", {})}>
              Cancel
            </Button>
            <Button variant="primary" onClick={form.submitForm}>
              Save
            </Button>
          </ActionRow>
        </div>
      </div>
    </div>
  );
};
