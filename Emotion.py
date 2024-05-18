import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from inference import get_model, InferencePipeline
from inference.core.interfaces.stream.sinks import render_boxes
import supervision as sv
from inference.core.interfaces.camera.entities import VideoFrame
import cv2
import subprocess

# Create a simple box annotator to use in our custom sink
annotator = sv.BoxAnnotator()

class ImageUploaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Emotion Detection")

        # Configure background color
        self.root.configure(bg="#81b29a")

        # Create a frame for camera/picture display
        self.display_frame = tk.Frame(root, bg="#81b29a")
        self.display_frame.pack()

        # Add a label for the small picture (logo)
        self.logo = Image.open("logo.png")  # Replace "logo.png" with the path to your small picture
        self.logo = self.logo.resize((50, 50))  # Resize small picture
        self.logo_image = ImageTk.PhotoImage(self.logo)
        self.small_picture_label = tk.Label(self.display_frame, image=self.logo_image, bg="#81b29a")
        self.small_picture_label.pack(side=tk.TOP, pady=5)  # Position small picture label at the top with some padding

        self.canvas = tk.Canvas(self.display_frame, width=400, height=400, bg="#f4f1de")
        self.canvas.pack()

        self.button_frame = tk.Frame(root, bg="#81b29a")
        self.button_frame.pack(pady=10)  # Added padding between buttons and label

        # Configure button color
        button_color = "#f2cc8f"  # Yellow

        # Configure font
        button_font = ("Arial", 10, "bold")
        
        self.upload_button = tk.Button(self.button_frame, text="🌸 Upload Image 🌸", command=self.upload_image, bg=button_color, relief=tk.RAISED, height=2, width=15, font=button_font)
        self.upload_button.pack(side=tk.LEFT, padx=10)

        self.webcam_button = tk.Button(self.button_frame, text="🌼 Turn on Webcam 🌼", command=self.turn_on_webcam, bg=button_color, relief=tk.RAISED, height=2, width=15, font=button_font)
        self.webcam_button.pack(side=tk.LEFT, padx=10)

        self.upload_video_button = tk.Button(self.button_frame, text="🌺 Upload Video 🌺", command=self.upload_video, bg=button_color, relief=tk.RAISED, height=2, width=15, font=button_font)
        self.upload_video_button.pack(side=tk.LEFT, padx=10)

        self.feeling_label = tk.Label(root, text="Feeling: ", bg="#e5e5e5", fg="black", font=("Arial", 12, "bold"))
        self.feeling_label.pack(pady=10)

        # Create a button to open app.py
        self.open_app_button = tk.Button(root, text="🍀 Click here for a link to our Website! 🍀", command=self.open_app, bg=button_color, relief=tk.RAISED, height=2, width=30, font=("Arial", 12, "bold"))
        self.open_app_button.pack(pady=10)  # Placed right under the feeling label

        self.current_video = None  # Placeholder for the currently displayed video
        
    def upload_image(self):
        file_path = filedialog.askopenfilename()

        if file_path:
            image = Image.open(file_path)
            self.current_video = None  # Clear current video

            # Resize image to fit the display screen
            image = self.resize_image(image, (400, 400))

            # Display resized image
            self.display_image(image)

            # Update feeling label
            emotion = self.extract_emotion_from_image(image)
            self.feeling_label.config(text="Feeling: " + emotion)

    def upload_video(self):
        file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4")])
        if file_path:
            self.current_video = file_path  # Store the path of the uploaded video

            # Display video frames
            self.display_video()

            # Update feeling label
            self.feeling_label.config(text="Uploaded Video: " + file_path)

            # Start inference on the uploaded video
            self.start_video_inference(file_path)

    def turn_on_webcam(self):
        self.feeling_label.config(text="Turning on Webcam...")
        
        pipeline = InferencePipeline.init(
            model_id="facial-emotion-detector/2",
            video_reference=0,
            on_prediction=self.on_prediction,
        )
        pipeline.start()
        pipeline.join()

    def extract_emotion_from_image(self, image):
        try:
            model = get_model(model_id="facial-emotion-detector/2", api_key="API_KEY")
            results = model.infer(image)

            detections = sv.Detections.from_inference(results[0].dict(by_alias=True, exclude_none=True))

            # Assuming the result is a dictionary with emotion as one of the keys
            for x in detections:
                emotion = x[5]['class_name']
                print(emotion)
            return emotion
        except Exception as e:
            print("Error:", e)
            return "Cannot Detect"

    def display_image(self, image):
        # Clear canvas
        self.canvas.delete("all")

        # Display image
        photo = ImageTk.PhotoImage(image)
        #self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        self.canvas.create_image(200, 200, anchor=tk.CENTER, image=photo)
        self.canvas.image = photo  # Keep a reference to avoid garbage collection

    def display_video(self):
        if self.current_video:
            cap = cv2.VideoCapture(self.current_video)
            while cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame = Image.fromarray(frame)
                    self.display_image(frame)
                    self.root.update_idletasks()
                else:
                    break
            cap.release()

    def start_video_inference(self, video_path):
        pipeline = InferencePipeline.init(
            model_id="facial-emotion-detector/2",
            video_reference=video_path,
            on_prediction=my_custom_sink,
        )
        pipeline.start()
        pipeline.join()

    def on_prediction(self, predictions: dict, video_frame: VideoFrame):
        labels = [p["class"] for p in predictions["predictions"]]
        detections = sv.Detections.from_inference(predictions)
        image = annotator.annotate(
            scene=video_frame.image.copy(), detections=detections, labels=labels
        )
        cv2.imshow("Predictions", image)
        cv2.waitKey(1)
        # Extract emotion from predictions and update feeling label
        emotion = predictions[0]['emotion']
        self.feeling_label.config(text="Feeling: " + emotion)

    def resize_image(self, image, size):
        """
        Resize the image to fit the given size while maintaining aspect ratio.
        """
        width, height = image.size
        ratio = min(size[0] / width, size[1] / height)
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        return image.resize((new_width, new_height))
        
    def open_app(self):
        # Open app.py using subprocess
        subprocess.Popen(["python3", "app.py"])

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageUploaderApp(root)
    root.mainloop()
