from flask import Flask, request
import sys
sys.path.append("..")
from audio import *
from fastai.vision import *
import scaper
import shutil

app = Flask(__name__)
# location where you will store uploaded files
data_dir = '/code/'
UPLOAD_FOLDER = data_dir+'foreground/upload/'
# augment files locations
fg_dir = data_dir+'foreground/'
bg_dir = data_dir+'background/'
augmented_dir = data_dir+'augmented/'
model_dir = data_dir+'model/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['wav'])

@app.route('/hello')
def hello_world():
    return '{ "msg" : "Hello, World!" }'

@app.route('/uploadAudioFile', methods=['POST'])
def uploadAudioFile():
    print("Posted file: {}".format(request.files['fileBlob']))
    file = request.files['fileBlob']
    if file and allowed_file(file.filename):
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        print('File successfully uploaded')
    return ""

@app.route('/predict')
def predictVoice():
    # we have to augment file to meet our config files slandered
    # convert file to have one channel
    augmentFile()
    # Load the model
    p_learn = load_learner(model_dir, 'hello.pkl')
    # prepare test dir use augmented file
    data_test = augmented_dir
    # prepare cfg file
    # make sure you add remove_silence = "trim", I recommend silence_threshold=6
    # but you can change the number based on your inputs
    # to remove silence please test using diff thresholds
    cfg = AudioConfig(cache=True, segment_size=None, max_to_pad=None, pad_mode="zeros",
                      resample_to=None, duration=1000, silence_threshold=6, use_spectro=True, remove_silence="trim")
    # clear cache if needed
    cfg.clear_cache()
    # prepare the databunch for test
    test = AudioList.from_folder(data_test, config=cfg).split_none().label_empty().databunch(bs=1)
    ai = test.open(test.items[0])
    preds_class, _, _ = p_learn.predict(ai)
    # print the predicted voice value
    print(preds_class)
    # prepare json
    return '{ "msg" : "'+str(preds_class)+'" }'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def augmentFile():
    hello_paths_txt, path = fetchPaths(UPLOAD_FOLDER)
    for n in range(len(path)):
        duration = findDuration(path[n])
        scapFiles(hello_paths_txt[n], augmented_dir, n_scapes=1, duration=duration)
    deleteJamsFolder()

def deleteJamsFolder():
    deletedir = augmented_dir+'jams/'
    shutil.rmtree(deletedir)

def findDuration(path):
    audio = open_audio(path)
    return round(audio.duration, 2)


def fetchPaths(given_dir):
    # audios = AudioList.from_folder(urban_ds_dir)
    posixpaths = get_files(path=given_dir, recurse=True)
    paths = []
    for item in posixpaths:
        _path = os.fspath(item)
        # add only audio files (.wav)
        if (_path.endswith('.wav')):
            paths.append(_path)
    return paths, posixpaths;


def createFolderIfNotPresent(folder):
    if os.path.exists(folder):
        print(folder + ' is present ')
    else:
        print(folder + ' is not present.')
        os.mkdir(folder)


# this function will create audio files with random noise in backround
def scapFiles(s_path, dest_dir, duration, n_scapes=10, ref_db=-20):
    file_name = s_path[s_path.rfind('/') + 1:s_path.rfind('.wav')]

    min_events = 1
    max_events = 9

    event_time_dist = 'truncnorm'
    event_time_mean = 5.0
    event_time_std = 2.0
    event_time_min = 0.0
    event_time_max = 10.0

    source_time_dist = 'const'
    source_time = 0.0

    event_duration_dist = 'uniform'
    event_duration_min = 0.5
    event_duration_max = 4.0

    snr_dist = 'uniform'
    snr_min = 6
    snr_max = 30

    pitch_dist = 'uniform'
    pitch_min = -3.0
    pitch_max = 3.0

    time_stretch_dist = 'uniform'
    time_stretch_min = 0.8
    time_stretch_max = 1.2

    for n in range(n_scapes):
        # sc = scaper.Scaper(duration,fg_dir,bg_dir)
        # flip fg and bg because add noise in forground and voice in background
        sc = scaper.Scaper(duration, bg_dir, fg_dir)
        sc.ref_db = ref_db

        # add person voice in background from upload folder
        sc.add_background(label=('const', 'upload'),
                          source_file=('choose', [s_path]),
                          source_time=('const', 0))

        # pick random number of events and create file
        n_events = np.random.randint(min_events, max_events + 1)
        for _ in range(n_events):
            sc.add_event(label=('choose', []),
                         source_file=('choose', []),
                         source_time=(source_time_dist, source_time),
                         event_time=(event_time_dist, event_time_mean, event_time_std, event_time_min, event_time_max),
                         event_duration=(event_duration_dist, event_duration_min, event_duration_max),
                         # I have to bring snr to below -20 so i can flip noice of bg and fg
                         # so it feels bg and fg noise have flipped the position
                         snr=('const', -20),
                         pitch_shift=(pitch_dist, pitch_min, pitch_max),
                         # don't add time streach it start with negative position
                         time_stretch=None)

        to_file = os.path.join(dest_dir + file_name + "/", file_name + "_augmented" + "_{:d}.wav".format(n))
        jamsfile = os.path.join(dest_dir + "jams/", file_name + "_jams_{:d}.jams".format(n))
        txtfile = os.path.join(dest_dir + "jams/", file_name + "_txt_{:d}.txt".format(n))

        createFolderIfNotPresent(dest_dir + file_name)
        createFolderIfNotPresent(dest_dir + "jams")

        # generate the file
        sc.generate(to_file, jamsfile,
                    allow_repeated_label=True,
                    # We have to allow file to reapeat becuase of limited number of hello files
                    allow_repeated_source=True,
                    reverb=0.1,
                    disable_sox_warnings=True,
                    no_audio=False)

if __name__ == '__main__':
    app.run()