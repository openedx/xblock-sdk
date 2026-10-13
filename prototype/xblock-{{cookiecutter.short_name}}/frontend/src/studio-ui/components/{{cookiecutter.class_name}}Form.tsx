import { Col, Form, Row } from "@openedx/paragon";
import { Field } from "formik";

export const {{cookiecutter.class_name}}Form = () => {
  return (
    <div className="{{cookiecutter.short_name}}-editor-form">
      <Row className="{{cookiecutter.short_name}}-editor-grid">
        <Form.Group
          className="{{cookiecutter.short_name}}-editor-field"
          as={Col}
          controlId="{{cookiecutter.short_name}}-form-display-name"
          xs={12}
        >
          <Form.Label>Display Name</Form.Label>
          <Field as={Form.Control} name="display_name" />
          <Form.Text muted>The label for this block, shown only in studio.</Form.Text>
        </Form.Group>
        <Form.Group className="{{cookiecutter.short_name}}-editor-field" as={Col} controlId="{{cookiecutter.short_name}}-form-code" xs={12}>
          <Form.Label>Code</Form.Label>
          <Field as={Form.Control} name="code" />
          <Form.Text muted>
            The code the increment button must send along with its request to increment. Will fail
            if there's a mismatch until the user refreshes.
          </Form.Text>
        </Form.Group>
      </Row>
    </div>
  );
};
