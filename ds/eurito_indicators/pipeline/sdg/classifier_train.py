import joblib

from eurito_indicators import PROJECT_DIR
from metaflow import FlowSpec, step, Parameter
from sentence_transformers import SentenceTransformer

from eurito_indicators.getters.sdg import load_annotated
from eurito_indicators.pipeline.sdg.classifier import make_sdg_pipeline


class SDGClassifierTrainFlow(FlowSpec):
    encoder = Parameter('encoder',
                        help='Transformer type to encode text',
                        required=True,
                        type=str)
    save_model = Parameter('save_model',
                        help='Saves model to outputs/models if True',
                        default=False,
                        type=bool
                        )
    test = Parameter('test',
                     help='Only trains a model for 2 SDGs if True',
                     default=False,
                     type=bool
                     )

    @step
    def start(self):
        """Starts the flow."""
        if self.test:
            self.sdgs = [1, 2]
        else:
            self.sdgs = list(range(1, 17))
        self.next(self.train_sdg_model, foreach='sdgs')

    @step
    def train_sdg_model(self):
        """Encodes training data and fits models."""
        self.sdg = self.input
        data = load_annotated(self.sdg)

        if self.test:
            data = data.sample(100)

        st = SentenceTransformer(self.encoder)
        encodings = st.encode(list(data['abstract']))

        self.pipe = make_sdg_pipeline(self.sdg)
        self.pipe.fit(encodings, data['label'])

        self.next(self.join)

    @step
    def join(self, inputs):
        """Joins results into a dictionary of models."""
        self.models = {input.sdg: input.pipe for input in inputs}

        if self.save_model:
            model_path = f'{PROJECT_DIR}/outputs/models/sdg_classifier.pkl'
            with open(model_path, 'wb') as fout:
                joblib.dump(self.models, fout)

        self.next(self.end)

    @step
    def end(self):
        """Ends the flow."""
        pass

if __name__ == '__main__':
    SDGClassifierTrainFlow()
