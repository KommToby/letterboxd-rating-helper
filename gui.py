from lttrbxd import Films
import tkinter as tk
from PIL import Image, ImageTk
import requests
from io import BytesIO
import time


def main():
    films = Films()
    if films.films:
        create_gui(films)
    else:
        print("Invalid username! please check your config.json file.")


def load_image(url: str):
    response = requests.get(url)
    img_data = response.content
    img = Image.open(BytesIO(img_data))
    photo = ImageTk.PhotoImage(img)
    return photo


def create_gui(films: Films):
    # Create default gui
    window = tk.Tk()
    window.title("Letterboxd Rating Helper")
    window.geometry("350x200")

    # lock the aspect ratio of the window
    window.resizable(False, False)

    # create an image label
    photo = load_image(
        "https://a.ltrbxd.com/resized/film-poster/5/4/2/7/7/3/542773-babylon-0-70-0-105-crop.jpg?v=75f0bfce72")
    image_label = tk.Label(window, image=photo)

    # create a label and entry for the movie name
    movie_name_label = tk.Label(
        text="Enter the name of the movie you want to rate")
    movie_name_entry = tk.Entry(width=30)

    # Create a submit button
    submit_button = tk.Button(window, text="Submit", command=lambda: handle_submit(
        window, films, movie_name_entry))

    # add the widgets
    image_label.place(relx=0.5, rely=0.35, anchor='center')  # center the image
    movie_name_label.place(relx=0.5, rely=0.6, anchor='center')
    movie_name_entry.place(relx=0.5, rely=0.75, anchor='center')
    submit_button.place(relx=0.5, rely=0.9, anchor='center')

    # start the gui
    window.mainloop()


def destroy_widgets(window: tk.Tk):
    for widget in window.winfo_children():
        widget.destroy()
    return window


def get_film(films: Films, rating: float):
    # get the film with the closest rating
    film = None
    for key, value in films.films.items():
        if value[0] == rating:
            film = key
            break
    # if film is still none, then we need to get the closest rating
    if film == None:
        return_film = None
        for key, value in films.films.items():
            if return_film == None:
                return_film = key
            else:
                if abs(value[0] - rating) < abs(films.films[return_film][0] - rating):
                    return_film = key
        film = return_film
    return film


def handle_submit(window: tk.Tk, films: Films, movie_name_entry):
    # first we destroy the widgets
    if type(movie_name_entry) != str:  # handles iteration
        movie_name = movie_name_entry.get().strip()
    else:
        movie_name = movie_name_entry
    window = destroy_widgets(window)

    # now we create new widgets, starting with getting an average rating film to compare
    film = get_film(films, films.rating)
    photo = load_image(films.films[film][1])
    image_label = tk.Label(window, image=photo)
    films.film_rating = films.films[film][0]
    films.films.pop(film)  # remove the film from the list for next loopp

    # create a label and entry for the movie name
    movie_name_label = tk.Label(
        text=f"Is {movie_name} better or worse than {film}?")
    better_button = tk.Button(window, text="Better", command=lambda: handle_better(
        window, films, movie_name, film))
    worse_button = tk.Button(window, text="Worse", command=lambda: handle_worse(
        window, films, movie_name, film))

    # add the widgets
    image_label.place(relx=0.5, rely=0.3, anchor='center')  # center the image
    movie_name_label.place(relx=0.5, rely=0.6, anchor='center')
    better_button.place(relx=0.3, rely=0.75, anchor='center')
    worse_button.place(relx=0.6, rely=0.75, anchor='center')

    # sleep for 1 second to allow photo to load
    time.sleep(0.25)
    # update the gui
    window.mainloop()


def handle_better(window: tk.Tk, films: Films, movie_name: str, film: str):
    films.counter += 1
    if films.counter < 25 and films.films != {}:  # 25 comparisons is good
        films.better += 1
        films.ratings.append(films.film_rating+1)
        films.rating = (
            (sum(films.ratings) / len(films.ratings)) + films.film_rating+1)/2
        handle_submit(window, films, movie_name)
    else:
        handle_end(window, films, movie_name, film)


def handle_worse(window: tk.Tk, films: Films, movie_name: str, film: str):
    films.counter += 1
    if films.counter < 25 and films.films != {}:  # 25 comparisons is good
        films.worse += 1
        films.ratings.append(films.film_rating-1)
        films.rating = (
            (sum(films.ratings) / len(films.ratings)) + films.film_rating-1)/2
        handle_submit(window, films, movie_name)
    else:
        handle_end(window, films, movie_name, film)


def handle_end(window: tk.Tk, films: Films, movie_name: str, film: str):
    films.rating = (sum(films.ratings) / len(films.ratings))
    if films.rating > 5:
        films.rating = 5
    else:
        # round up to the nearest 0.5
        films.rating = round(films.rating * 2) / 2
    # print(f"Your rating for {movie_name} is {round(films.rating)}")
    window = destroy_widgets(window)
    rating_text = f"Your rating for {movie_name} is:"
    rating_label = tk.Label(window, text=rating_text, font=("Arial", 16))
    rating_number = tk.Label(
        window, text=f"{films.rating}/5", font=("Arial", 64, "bold"))

    rating_label.place(relx=0.5, rely=0.2, anchor='center')
    rating_number.place(relx=0.5, rely=0.525, anchor='center')

    # update the gui
    window.mainloop()


if __name__ == "__main__":
    main()
