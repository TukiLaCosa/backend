# import os
# import pygame
# import time


# def show_initial_image():
#     # Path of the image I want to display
#     image_path = "./app/resources/stay_away.png"

#     # Path of the audio file
#     audio_path = "./app/resources/stay_away.mp3"

#     # pygame configuration
#     pygame.init()
#     window = pygame.display.set_mode((400, 300), pygame.NOFRAME)

#     # Load the image
#     image = pygame.image.load(image_path)

#     # Get the width and height of the window
#     window_width, window_height = window.get_size()

#     # Scale the image to the size of the window
#     image = pygame.transform.scale(image, (window_width, window_height))

#     # Show the image in the window
#     window.blit(image, (0, 0))
#     pygame.display.flip()

#     # Play audio file
#     pygame.mixer.init()
#     pygame.mixer.music.load(audio_path)
#     pygame.mixer.music.play()

#     # Wait 6 seconds
#     time.sleep(6)

#     # Close the window
#     pygame.quit()
