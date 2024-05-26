import React from 'react';
import { Editor, EditorState, ContentState, convertFromHTML } from 'draft-js';

class ReadOnlyRichText extends React.Component {
  constructor(props) {
    super(props);
    this.state = this.initStateFromProps(props);
  }

  initStateFromProps(props) {
    if (typeof props.initialValue === 'string') {
      const blocksFromHtml = convertFromHTML(props.initialValue);
      const state = ContentState.createFromBlockArray(
        blocksFromHtml.contentBlocks,
        blocksFromHtml.entityMap
      );

      return {
        editorState: EditorState.createWithContent(state),
      };
    } else {
      console.error('Invalid initialValue provided to ReadOnlyRichText. It should be an HTML string.');
      return {
        editorState: EditorState.createEmpty(),
      };
    }
  }

  componentDidUpdate(prevProps) {
    if (prevProps.initialValue !== this.props.initialValue) {
      console.log('Received new initialValue:', this.props.initialValue);
      this.setState(this.initStateFromProps(this.props));
    }
  }

  render() {
    const { editorState } = this.state;

    const customStyleMap = {};

    return (
      <div className="read-only-rich-text-container">
        <Editor
          readOnly
          editorState={editorState}
          customStyleMap={customStyleMap}
          handleKeyCommand={() => false}
          onBlur={() => null}
          onFocus={() => null}
          stripPastedStyles
        />
      </div>
    );
  }
}

export default ReadOnlyRichText;